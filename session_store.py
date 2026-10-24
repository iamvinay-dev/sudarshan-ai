# -*- coding: utf-8 -*-
"""
session_store.py
----------------
Conversation memory for every pilgrim, saved in Supabase (table "conversations").

Why: the server can run several worker processes and restarts often. Memory kept in
RAM is lost or split between workers, so the bot "forgot" what it had just asked
(for example the complaint menu) and answered the next message like a new chat.

What is remembered per pilgrim (keyed by the same anonymous hash as the pilgrim ID,
never by phone number):
    history          the last 5 exchanges (personal data removed before saving)
    flow             an active complaint / feedback conversation
    last_lang        language used in the last message
    forced_lang      language the pilgrim chose by typing e.g. "Kannada"
    last_unanswered  the last question the bot could not answer
    stats            counters used to decide when to ask "was your question solved?"

A conversation that is idle for 12 hours starts fresh.

Usage (app.py):  ss.begin(phone) ... ss.cur() ... ss.end()
If Supabase is down, a copy in RAM is used, so the bot keeps working.
"""

import time
import random
import logging
import threading
from datetime import datetime, timedelta, timezone

import db

log = logging.getLogger("sudarshan-ai.session")

IDLE_RESET = 12 * 3600
KEEP_DAYS = 3
MAX_LOCAL = 3000

_tl = threading.local()
_local = {}


def _blank():
    return {"flow": None, "history": [], "last_lang": None, "forced_lang": None,
            "last_unanswered": None, "stats": {}, "updated": time.time()}


def _normalize(raw):
    s = _blank()
    if isinstance(raw, dict):
        for k in s:
            if k in raw:
                s[k] = raw[k]
    if time.time() - float(s.get("updated") or 0) > IDLE_RESET:
        s["history"], s["flow"] = [], None
    if not isinstance(s["history"], list):
        s["history"] = []
    if not isinstance(s["stats"], dict):
        s["stats"] = {}
    return s


def begin(phone: str) -> dict:
    """Load this pilgrim's conversation (one database read). Safe to call twice."""
    if getattr(_tl, "phone", None) == phone and getattr(_tl, "session", None) is not None:
        return _tl.session
    raw = None
    if db.logging_enabled():
        rows = db._json(db._request("GET", "conversations", timeout=3, params={
            "select": "data", "phone_hash": f"eq.{db.phone_hash(phone)}", "limit": "1"}))
        raw = rows[0].get("data") if rows else (_local.get(phone) if rows is None else None)
    else:
        raw = _local.get(phone)
    _tl.phone, _tl.session = phone, _normalize(raw)
    return _tl.session


def cur() -> dict:
    """The conversation being handled right now."""
    s = getattr(_tl, "session", None)
    if s is None:                       # used outside a webhook (tests)
        s = _tl.session = _blank()
    return s


def end() -> None:
    """Save the conversation (one database write)."""
    s, phone = getattr(_tl, "session", None), getattr(_tl, "phone", None)
    _tl.session = _tl.phone = None
    if s is None or phone is None:
        return
    s["updated"] = time.time()
    _local[phone] = s
    while len(_local) > MAX_LOCAL:
        _local.pop(next(iter(_local)))
    if db.logging_enabled():
        now = datetime.now(timezone.utc)
        db._request("POST", "conversations", params={"on_conflict": "phone_hash"}, timeout=4,
                    body={"phone_hash": db.phone_hash(phone), "data": s, "updated_at": now.isoformat()},
                    prefer="return=minimal,resolution=merge-duplicates")
        if random.random() < 0.01:      # tidy up old conversations now and then
            old = (now - timedelta(days=KEEP_DAYS)).isoformat()
            db.submit(db._request, "DELETE", "conversations", params={"updated_at": f"lt.{old}"},
                      prefer="return=minimal")
