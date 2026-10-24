# -*- coding: utf-8 -*-
"""
db.py
-----
Supabase layer for Sudarshan AI (Phase 2 + Phase 3).

What this file does:
    1. Pilgrim privacy   - phone number -> HMAC hash -> pilgrim code like '#1001'.
                           The real number is never written to the database or logs.
    2. Query logging     - every question + reply is saved (text is redacted first),
                           in a background thread so pilgrims never wait for it.
    3. Answer cache      - repeated AI answers are served from memory / Supabase.
    4. Knowledge base    - loaded from Supabase every 5 minutes (falls back to the
                           Python file if Supabase is unreachable).
    5. One-time migration of knowledge_base.py into Supabase.

Talks to Supabase through its REST API using only `requests` (no extra packages).
EVERY database call is wrapped so that a database problem can never stop the bot
from answering pilgrims.

Environment variables:
    SUPABASE_URL           e.g. https://abcdxyz.supabase.co
    SUPABASE_SERVICE_KEY   the SECRET key (server only - never share it)
    PHONE_HASH_SECRET      long random text; set once and NEVER change it
    CACHE_TTL_HOURS        optional, default 168 (7 days)
"""

import os
import re
import json
import time
import hmac
import hashlib
import logging
import threading
from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone

import requests

log = logging.getLogger("sudarshan-ai.db")

SUPABASE_URL = os.environ.get("SUPABASE_URL", "").strip().rstrip("/")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_KEY", "").strip()
PHONE_HASH_SECRET = os.environ.get("PHONE_HASH_SECRET", "").strip()

try:
    CACHE_TTL_HOURS = int(os.environ.get("CACHE_TTL_HOURS", "168"))
except ValueError:
    CACHE_TTL_HOURS = 168


def db_configured() -> bool:
    return bool(SUPABASE_URL and SUPABASE_KEY)


def logging_enabled() -> bool:
    """Pilgrim logging needs the hash secret too (otherwise IDs would reset)."""
    return db_configured() and bool(PHONE_HASH_SECRET)


# ---------------------------------------------------------------------------
# Low-level REST helper with a simple circuit breaker:
# after 3 failures in a row, skip the database for 30 seconds.
# ---------------------------------------------------------------------------
_lock = threading.Lock()
_fail_count = 0
_blocked_until = 0.0
_executor = ThreadPoolExecutor(max_workers=4)


def submit(fn, *args, **kwargs) -> None:
    """Run fn in the background (never blocks the WhatsApp reply)."""
    try:
        _executor.submit(_safe, fn, *args, **kwargs)
    except Exception as exc:  # noqa: BLE001
        log.error("Could not start background task: %s", type(exc).__name__)


def _safe(fn, *args, **kwargs):
    try:
        return fn(*args, **kwargs)
    except Exception as exc:  # noqa: BLE001
        log.error("Background task failed: %s", type(exc).__name__)
        return None


def _record(ok: bool) -> None:
    global _fail_count, _blocked_until
    with _lock:
        if ok:
            _fail_count = 0
            return
        _fail_count += 1
        if _fail_count >= 3:
            _blocked_until = time.time() + 30
            _fail_count = 0
            log.warning("Supabase unreachable - pausing database calls for 30s.")


def _request(method, path, params=None, body=None, prefer=None, timeout=6):
    if not db_configured() or time.time() < _blocked_until:
        return None
    headers = {"apikey": SUPABASE_KEY, "Content-Type": "application/json"}
    if not SUPABASE_KEY.startswith("sb_"):          # legacy JWT-style keys
        headers["Authorization"] = f"Bearer {SUPABASE_KEY}"
    if prefer:
        headers["Prefer"] = prefer
    try:
        resp = requests.request(
            method, f"{SUPABASE_URL}/rest/v1/{path}",
            params=params, json=body, headers=headers, timeout=timeout,
        )
    except Exception as exc:  # noqa: BLE001
        _record(False)
        log.error("Supabase request failed: %s", type(exc).__name__)
        return None
    if resp.status_code >= 500:
        _record(False)
        log.error("Supabase server error [%s]", resp.status_code)
        return None
    _record(True)
    if resp.status_code >= 400:
        log.error("Supabase rejected request to %s [%s]: %s",
                  path, resp.status_code, resp.text[:200])
        return None
    return resp


def _json(resp):
    if resp is None:
        return None
    try:
        return resp.json()
    except Exception:  # noqa: BLE001
        return None


# ---------------------------------------------------------------------------
# Privacy helpers
# ---------------------------------------------------------------------------
def phone_hash(phone: str) -> str:
    digits = re.sub(r"\D", "", str(phone))
    return hmac.new(PHONE_HASH_SECRET.encode(), digits.encode(), hashlib.sha256).hexdigest()


_EMAIL = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
_LONG_NUMBER = re.compile(r"(?<!\d)\+?\d(?:[ \-.]?\d){9,}(?!\d)")          # phones, Aadhaar
_ID_LIKE = re.compile(r"\b(?=[A-Za-z0-9\-]*\d)(?=[A-Za-z0-9\-]*[A-Za-z])[A-Za-z0-9\-]{8,}\b")


def redact(text: str) -> str:
    """Remove phone numbers, Aadhaar-like numbers, emails and booking-ID-like
    strings from text BEFORE it is stored."""
    text = _EMAIL.sub("[redacted]", text or "")
    text = _LONG_NUMBER.sub("[redacted]", text)
    text = _ID_LIKE.sub("[redacted]", text)
    return text


def normalize_key(text: str) -> str:
    t = re.sub(r"[^\w\s\u0c00-\u0c7f]", " ", (text or "").lower())
    return re.sub(r"\s+", " ", t).strip()


# ---------------------------------------------------------------------------
# Query logging (runs in the background)
# ---------------------------------------------------------------------------
def log_interaction(phone, text, reply, meta, wa_message_id=None, response_ms=None):
    """Save one question/reply under an anonymous pilgrim code."""
    if not logging_enabled():
        return None
    lang = (meta or {}).get("language") or "en"

    rows = _json(_request(
        "POST", "rpc/get_or_create_pilgrim",
        body={"p_hash": phone_hash(phone), "p_lang": lang},
    ))
    if not rows:
        return None
    pilgrim_id, pilgrim_code = rows[0].get("out_id"), rows[0].get("out_code")

    clean_text = redact(text)[:500]
    row = {
        "wa_message_id": wa_message_id,
        "pilgrim_id": pilgrim_id,
        "query_text": clean_text,
        "normalized_text": normalize_key(clean_text)[:300],
        "reply_text": (reply or "")[:4000],
        "source": (meta or {}).get("source", "unknown"),
        "category": (meta or {}).get("category"),
        "matched_question": (meta or {}).get("matched_question"),
        "language": lang,
        "response_ms": response_ms,
        "answered": bool((meta or {}).get("answered", True)),
    }
    resp = _request(
        "POST", "queries", params={"on_conflict": "wa_message_id"}, body=row,
        prefer="return=minimal,resolution=ignore-duplicates",
    )
    if resp is not None:
        log.info("Query logged for %s (%s)", pilgrim_code, row["source"])
    return pilgrim_code


# ---------------------------------------------------------------------------
# Answer cache (AI answers only): memory first, then Supabase
# ---------------------------------------------------------------------------
_MEM_MAX = 500
_MEM_SECONDS = 3600
_mem = OrderedDict()   # key -> (reply, expires_ts)


def cache_key(text: str, lang: str) -> str:
    return hashlib.sha256(f"{normalize_key(text)}|{lang}".encode()).hexdigest()


def _mem_put(key, reply):
    _mem[key] = (reply, time.time() + _MEM_SECONDS)
    _mem.move_to_end(key)
    while len(_mem) > _MEM_MAX:
        _mem.popitem(last=False)


def cache_get(key: str):
    """Returns the cached reply text, or None."""
    item = _mem.get(key)
    if item:
        if item[1] > time.time():
            _mem.move_to_end(key)
            return item[0]
        _mem.pop(key, None)

    if not db_configured():
        return None
    now_iso = datetime.now(timezone.utc).isoformat()
    rows = _json(_request(
        "GET", "answer_cache",
        params={"select": "reply_text,hits", "cache_key": f"eq.{key}",
                "expires_at": f"gt.{now_iso}", "limit": "1"},
        timeout=3,
    ))
    if not rows:
        return None
    reply = rows[0].get("reply_text")
    if not reply:
        return None
    _mem_put(key, reply)
    submit(_bump_hits, key, int(rows[0].get("hits") or 0) + 1)
    return reply


def _bump_hits(key, hits):
    _request("PATCH", "answer_cache", params={"cache_key": f"eq.{key}"},
             body={"hits": hits}, prefer="return=minimal")


def cache_set(key: str, reply: str) -> None:
    _mem_put(key, reply)
    submit(_cache_store, key, reply)


def _cache_store(key, reply):
    now = datetime.now(timezone.utc)
    _request(
        "POST", "answer_cache", params={"on_conflict": "cache_key"},
        body={"cache_key": key, "reply_text": reply, "hits": 0,
              "created_at": now.isoformat(),
              "expires_at": (now + timedelta(hours=CACHE_TTL_HOURS)).isoformat()},
        prefer="return=minimal,resolution=merge-duplicates",
    )


def cache_clear() -> None:
    _mem.clear()
    _request("DELETE", "answer_cache",
             params={"created_at": "gt.1970-01-01T00:00:00+00:00"},
             prefer="return=minimal")


# ---------------------------------------------------------------------------
# Knowledge base: Supabase -> memory
# ---------------------------------------------------------------------------
_kb_sig = None
_kb_thread_started = False


def _get_all(table, params):
    """Fetch every row of a table (1000 per page)."""
    out, offset = [], 0
    while True:
        page = _json(_request("GET", table,
                              params={**params, "limit": "1000", "offset": str(offset)}))
        if page is None:
            return None
        out.extend(page)
        if len(page) < 1000:
            return out
        offset += 1000


def apply_kb_rows(kb, categories, qas) -> bool:
    """Swap the live knowledge base (inside knowledge_base.py) for Supabase rows.
    Refuses to apply anything incomplete, so a half-filled table can never
    break the bot."""
    new_kb, order = {}, []
    for c in sorted(categories, key=lambda r: r.get("sort_order") if r.get("sort_order") is not None else 999):
        key = c.get("key")
        if not key:
            continue
        order.append(key)
        new_kb[key] = {
            "title": c.get("title") or key,
            "summary": c.get("summary_en") or "",
            "summary_te": c.get("summary_te") or "",
            "qas": [],
        }
    for r in qas:
        if r.get("active") is False:
            continue
        cat = new_kb.get(r.get("category_key"))
        if cat and r.get("question") and r.get("answer"):
            cat["qas"].append({"q": r["question"], "a": r["answer"]})

    if not order or any(not new_kb[k]["qas"] for k in order):
        log.warning("Supabase knowledge base incomplete - keeping the built-in one.")
        return False

    kb.KNOWLEDGE_BASE.clear()
    kb.KNOWLEDGE_BASE.update(new_kb)
    kb.MENU_ORDER[:] = order
    kb.CATEGORY_MAP.clear()
    kb.CATEGORY_MAP.update({str(i + 1): k for i, k in enumerate(order)})
    kb._QA_INDEX[:] = [(k, qa["q"], qa["a"]) for k in order for qa in new_kb[k]["qas"]]
    return True


def refresh_kb(kb) -> bool:
    global _kb_sig
    cats = _get_all("kb_categories", {"select": "key,title,summary_en,summary_te,sort_order",
                                      "order": "sort_order.asc"})
    qas = _get_all("kb_qas", {"select": "category_key,question,answer,active",
                              "active": "eq.true", "order": "id.asc"})
    if not cats or not qas:
        return False
    sig = hashlib.sha256(json.dumps([cats, qas], sort_keys=True,
                                    ensure_ascii=False).encode()).hexdigest()
    if sig == _kb_sig:
        return True
    if not apply_kb_rows(kb, cats, qas):
        return False
    changed = _kb_sig is not None
    _kb_sig = sig
    log.info("Knowledge base loaded from Supabase: %d categories, %d Q&As.", len(cats), len(qas))
    if changed:
        cache_clear()      # answers may be outdated now
    return True


def start_kb_refresh_loop(kb, interval_seconds: int = 300) -> None:
    global _kb_thread_started
    if _kb_thread_started or not db_configured():
        return
    _kb_thread_started = True

    def loop():
        while True:
            try:
                refresh_kb(kb)
            except Exception as exc:  # noqa: BLE001
                log.error("Knowledge base refresh failed: %s", type(exc).__name__)
            time.sleep(interval_seconds)

    threading.Thread(target=loop, daemon=True).start()


# ---------------------------------------------------------------------------
# One-time migration: knowledge_base.py -> Supabase
# ---------------------------------------------------------------------------
def migrate_kb(kb, force: bool = False):
    """Copy the Python knowledge base into Supabase. Returns (ok, message)."""
    if not db_configured():
        return False, "Supabase is not configured (SUPABASE_URL / SUPABASE_SERVICE_KEY)."

    existing = _json(_request("GET", "kb_qas", params={"select": "id", "limit": "1"}))
    if existing is None:
        return False, "Could not reach Supabase. Check the URL and key."
    if existing and not force:
        return False, "kb_qas already has data. Add &force=1 to the link to replace it."

    cats, qas = [], []
    for i, key in enumerate(kb.MENU_ORDER):
        c = kb.KNOWLEDGE_BASE[key]
        cats.append({"key": key, "title": c.get("title"), "summary_en": c.get("summary"),
                     "summary_te": c.get("summary_te"), "sort_order": i})
        for qa in c["qas"]:
            qas.append({"category_key": key, "question": qa["q"], "answer": qa["a"], "active": True})

    if existing and force:
        if _request("DELETE", "kb_qas", params={"id": "gt.0"}, prefer="return=minimal") is None:
            return False, "Could not clear the old Q&As."

    if _request("POST", "kb_categories", params={"on_conflict": "key"}, body=cats,
                prefer="return=minimal,resolution=merge-duplicates") is None:
        return False, "Could not save categories."
    for start in range(0, len(qas), 100):
        if _request("POST", "kb_qas", body=qas[start:start + 100],
                    prefer="return=minimal") is None:
            return False, f"Stopped while saving Q&As (batch starting at {start}). Add &force=1 and retry."

    return True, f"Saved {len(cats)} categories and {len(qas)} Q&As to Supabase."
