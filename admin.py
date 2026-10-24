# -*- coding: utf-8 -*-
"""
admin.py
--------
Admin website for Sudarshan AI  (open it at  /admin ).

ONE file, NO new packages. It adds:
    - Strong login (hashed passwords, lockout, rate limit, CSRF, secure cookies,
      30-minute idle timeout, security headers, audit log)
    - Live dashboard (refreshes every 5 seconds)
    - Questions list with filters + CSV export
    - Question detail page and Pilgrim detail page
    - Change-password page

PRIVACY: this file never reads the phone_hash / phone_enc columns. Every database
request below asks for an explicit list of safe columns. Pilgrims appear only as
codes like #1001. Question text was already redacted before it was stored.

Environment variables (set in Render > Environment):
    SECRET_KEY                long random text, at least 32 characters
    ADMIN_BOOTSTRAP_USER      first admin username   (used only when no admin exists)
    ADMIN_BOOTSTRAP_PASSWORD  first admin password   (must change it at first login)
"""

import os
import re
import io
import csv
import time
import hmac
import secrets
import logging
import threading
from collections import Counter
from datetime import datetime, timedelta, timezone, date
from functools import wraps

from flask import (Blueprint, request, session, redirect, url_for, jsonify,
                   make_response, flash, get_flashed_messages, abort, g,
                   has_request_context)
from jinja2 import Environment, DictLoader
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.middleware.proxy_fix import ProxyFix

import db

log = logging.getLogger("sudarshan-ai.admin")

SECRET_KEY = os.environ.get("SECRET_KEY", "").strip()
ADMIN_ENABLED = len(SECRET_KEY) >= 32

IDLE_SECONDS = 30 * 60          # log out after 30 minutes without clicking
MAX_FAILED = 5                  # wrong passwords before the account is locked
LOCK_MINUTES = 15
PAGE_SIZE = 50
CSV_MAX_ROWS = 20000
STATS_ROWS = 5000               # newest rows used for dashboard numbers (last 30 days)
IST = timezone(timedelta(hours=5, minutes=30))
UTC = timezone.utc
CHART_JS = "https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"

SOURCES = ["menu", "greeting", "direct", "cache", "ai", "guardrail", "fallback"]
CATEGORIES = ["darshan", "accommodation", "transport", "history", "rules", "annadanam",
              "help", "offtopic", "identity", "injection", "smalltalk", "unknown"]
LANGS = ["en", "te"]
CATEGORY_LABELS = {"offtopic": "Off-topic", "help": "Help & contact", "rules": "Dress code & rules",
                   "darshan": "Darshan & tickets", "annadanam": "Annadanam & laddu"}
SOURCE_LABELS = {"menu": "Menu", "greeting": "Greeting", "direct": "Direct answer",
                 "cache": "Cache", "ai": "AI", "guardrail": "Guardrail", "fallback": "Fallback"}
LANG_LABELS = {"en": "English", "te": "Telugu"}

bp = Blueprint("admin", __name__, url_prefix="/admin")


class DBDown(Exception):
    pass


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------
def now_utc():
    return datetime.now(UTC)


def iso(dt):
    return dt.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%S.%f+00:00")


def parse_ts(s):
    """Parse a Supabase timestamp (handles 5-digit fractions and 'Z')."""
    if not s:
        return None
    try:
        s = str(s).replace("Z", "+00:00")
        m = re.match(r"(.*?\.)(\d+)(.*)$", s)
        if m:
            s = m.group(1) + (m.group(2) + "000000")[:6] + m.group(3)
        d = datetime.fromisoformat(s)
        if d.tzinfo is None:
            d = d.replace(tzinfo=UTC)
        return d
    except Exception:  # noqa: BLE001
        return None


def fmt_ist(value, seconds=False):
    d = value if isinstance(value, datetime) else parse_ts(value)
    if not d:
        return "-"
    return d.astimezone(IST).strftime("%d %b %Y, %I:%M:%S %p" if seconds else "%d %b %Y, %I:%M %p")


def parse_date(text):
    try:
        return datetime.strptime((text or "").strip(), "%Y-%m-%d").date()
    except ValueError:
        return None


def ist_midnight_utc(d):
    return datetime(d.year, d.month, d.day, tzinfo=IST).astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def client_ip():
    if not has_request_context():
        return "system"
    xff = request.headers.get("X-Forwarded-For", "")
    ip = xff.split(",")[0].strip() if xff else (request.remote_addr or "")
    return ip[:60] or "unknown"


# ---------------------------------------------------------------------------
# Database helpers (all through db.py, so the circuit breaker still protects us)
# ---------------------------------------------------------------------------
def _get(table, params, timeout=8):
    return db._json(db._request("GET", table, params=params, timeout=timeout))


def _count(table, params=None):
    p = {"select": "id", "limit": "1"}
    if params:
        p.update(params)
    resp = db._request("GET", table, params=p, prefer="count=exact", timeout=8)
    if resp is None:
        return None
    try:
        return int(resp.headers.get("Content-Range", "").split("/")[-1])
    except ValueError:
        return None


def _fetch_rows(table, params, max_rows):
    """Fetch up to max_rows rows (1000 per request). Returns (rows, truncated)."""
    out, offset = [], 0
    while len(out) < max_rows:
        size = min(1000, max_rows - len(out))
        page = _get(table, {**params, "limit": str(size), "offset": str(offset)}, timeout=12)
        if page is None:
            return (out or None), False
        out.extend(page)
        if len(page) < size:
            return out, False
        offset += size
    return out, True


_code_cache = {}


def codes_for(ids):
    """pilgrim id -> '#1001'. Only id and pilgrim_code are ever requested."""
    ids = {i for i in ids if isinstance(i, int)}
    missing = [i for i in ids if i not in _code_cache]
    for start in range(0, len(missing), 200):
        chunk = missing[start:start + 200]
        rows = _get("pilgrims", {"select": "id,pilgrim_code",
                                 "id": "in.(" + ",".join(str(i) for i in chunk) + ")"})
        for r in rows or []:
            _code_cache[r["id"]] = r["pilgrim_code"]
    if len(_code_cache) > 20000:
        _code_cache.clear()
    return {i: _code_cache.get(i, "#?") for i in ids}


def _audit_write(admin_id, event, ip):
    db._request("POST", "admin_audit", body={"admin_id": admin_id, "event": event[:120], "ip": ip},
                prefer="return=minimal")


def audit(admin_id, event, ip=None):
    db.submit(_audit_write, admin_id, event, ip or client_ip())


# ---------------------------------------------------------------------------
# Password rules
# ---------------------------------------------------------------------------
PASSWORD_HELP = "At least 12 characters, with a capital letter, a small letter, a number and a symbol."
_WEAK_PARTS = ("password", "passw0rd", "admin", "welcome", "qwerty", "letmein", "123456",
               "iloveyou", "tirumala", "tirupati", "venkatesa", "sudarshan", "govinda", "balaji", "ttd")


def password_problem(pw, username=""):
    if len(pw) < 12:
        return "Password must be at least 12 characters."
    if len(pw) > 128:
        return "Password is too long (maximum 128 characters)."
    if not re.search(r"[a-z]", pw) or not re.search(r"[A-Z]", pw):
        return "Password needs both capital and small letters."
    if not re.search(r"\d", pw):
        return "Password needs at least one number."
    if not re.search(r"[^A-Za-z0-9]", pw):
        return "Password needs at least one symbol (for example ! @ # $ %)."
    low = pw.lower()
    if username and username.lower() in low:
        return "Password must not contain your username."
    if any(w in low for w in _WEAK_PARTS):
        return "That password is too easy to guess. Avoid common words and names."
    return None


def make_hash(pw):
    return generate_password_hash(pw, method="pbkdf2:sha256:600000")


_dummy = None


def _dummy_hash():
    global _dummy
    if _dummy is None:
        _dummy = make_hash(secrets.token_urlsafe(12))
    return _dummy


# ---------------------------------------------------------------------------
# First admin (created from environment variables, no terminal needed)
# ---------------------------------------------------------------------------
_boot_lock = threading.Lock()
_boot_done = False


def ensure_bootstrap():
    """If NO admin exists yet, create one from ADMIN_BOOTSTRAP_USER / _PASSWORD."""
    global _boot_done
    if _boot_done or not ADMIN_ENABLED or not db.db_configured():
        return
    with _boot_lock:
        if _boot_done:
            return
        user = os.environ.get("ADMIN_BOOTSTRAP_USER", "").strip().lower()[:60]
        pw = os.environ.get("ADMIN_BOOTSTRAP_PASSWORD", "")
        if not user or not pw:
            _boot_done = True
            return
        existing = _get("admin_users", {"select": "id", "limit": "1"})
        if existing is None:
            return                      # database not reachable now - try again later
        _boot_done = True
        if existing:
            return
        problem = password_problem(pw, user)
        if problem:
            log.error("Admin NOT created: ADMIN_BOOTSTRAP_PASSWORD is too weak. %s", problem)
            return
        resp = db._request("POST", "admin_users", prefer="return=minimal", body={
            "username": user, "password_hash": make_hash(pw), "must_change_password": True})
        if resp is not None:
            log.info("First admin '%s' created. Password change is required at first login.", user)
            audit(None, "admin_created_from_bootstrap", "system")


# ---------------------------------------------------------------------------
# Login protection: CSRF, rate limit, sessions
# ---------------------------------------------------------------------------
_login_hits = {}


def rate_limited(ip, limit=5, window=60):
    now = time.time()
    hits = [t for t in _login_hits.get(ip, []) if now - t < window]
    limited = len(hits) >= limit
    if not limited:
        hits.append(now)
    _login_hits[ip] = hits
    if len(_login_hits) > 2000:
        for k in [k for k, v in _login_hits.items() if not v or now - v[-1] > window]:
            _login_hits.pop(k, None)
    return limited


def csrf_token():
    return session.setdefault("csrf", secrets.token_urlsafe(32))


def csrf_ok():
    sent = request.form.get("csrf_token", "")
    real = session.get("csrf", "")
    return bool(real) and hmac.compare_digest(sent.encode(), real.encode())


_user_cache = {}


def current_user():
    """The logged-in admin row, or None. Raises DBDown if the database is unreachable."""
    uid = session.get("admin_id")
    if not uid:
        return None
    if time.time() - session.get("last_active", 0) > IDLE_SECONDS:
        session.clear()
        return None
    cached = _user_cache.get(uid)
    if cached and cached[1] > time.time():
        row = cached[0]
    else:
        rows = _get("admin_users", {"select": "id,username,must_change_password",
                                    "id": f"eq.{uid}", "limit": "1"})
        if rows is None:
            raise DBDown()
        if not rows:
            session.clear()
            return None
        row = rows[0]
        _user_cache[uid] = (row, time.time() + 15)
    if not request.path.startswith("/admin/api/"):      # background polling must not keep us logged in
        session["last_active"] = int(time.time())
    return row


def login_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        is_api = request.path.startswith("/admin/api/")
        try:
            user = current_user()
        except DBDown:
            if is_api:
                return jsonify(error="database"), 503
            return render("message.html", title="Please wait",
                          text="The database is not reachable right now. Try again in a minute."), 503
        if not user:
            if is_api:
                return jsonify(error="login"), 401
            return redirect(url_for("admin.login"))
        g.user = user
        if user.get("must_change_password") and request.endpoint not in ("admin.change_password", "admin.logout"):
            return redirect(url_for("admin.change_password"))
        return view(*args, **kwargs)
    return wrapper


@bp.before_request
def _gate():
    if not ADMIN_ENABLED:
        abort(404)
    if not db.db_configured():
        return render("message.html", title="Not ready", text="The database is not configured."), 503
    ensure_bootstrap()


@bp.after_request
def _headers(resp):
    resp.headers["Cache-Control"] = "no-store"
    resp.headers["X-Frame-Options"] = "DENY"
    resp.headers["X-Content-Type-Options"] = "nosniff"
    resp.headers["Referrer-Policy"] = "no-referrer"
    resp.headers["X-Robots-Tag"] = "noindex, nofollow"
    resp.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    resp.headers["Content-Security-Policy"] = (
        "default-src 'self'; script-src 'self' https://cdnjs.cloudflare.com; "
        "style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'; "
        "base-uri 'none'; form-action 'self'; frame-ancestors 'none'")
    return resp


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------
def render(name, **ctx):
    ctx.setdefault("user", g.get("user"))
    ctx.setdefault("messages", get_flashed_messages(with_categories=True))
    ctx.setdefault("charts", False)
    ctx["chartjs"] = CHART_JS
    return make_response(_env.get_template(name).render(**ctx))


# ---------------------------------------------------------------------------
# Login / logout / change password
# ---------------------------------------------------------------------------
@bp.route("/")
def index():
    return redirect(url_for("admin.dashboard"))


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render("login.html")

    if not csrf_ok():
        flash("Please try again.", "error")
        return redirect(url_for("admin.login"))
    ip = client_ip()
    if rate_limited(ip):
        return render("message.html", title="Too many tries",
                      text="Too many login attempts. Please wait one minute and try again."), 429

    username = request.form.get("username", "").strip().lower()[:60]
    password = request.form.get("password", "")[:200]
    rows = _get("admin_users", {
        "select": "id,username,password_hash,must_change_password,failed_attempts,locked_until",
        "username": f"eq.{username}", "limit": "1"}) if username else []
    if rows is None:
        flash("The service is busy. Please try again in a minute.", "error")
        return redirect(url_for("admin.login"))
    row = rows[0] if rows else None

    now = now_utc()
    until = parse_ts(row.get("locked_until")) if row else None
    locked = bool(until and until > now)

    if row and not locked and check_password_hash(row["password_hash"], password):
        db._request("PATCH", "admin_users", params={"id": f"eq.{row['id']}"}, prefer="return=minimal",
                    body={"failed_attempts": 0, "locked_until": None, "last_login": iso(now)})
        session.clear()                                   # fresh session after login
        session["admin_id"] = row["id"]
        session["last_active"] = int(time.time())
        session["csrf"] = secrets.token_urlsafe(32)
        _user_cache.pop(row["id"], None)
        audit(row["id"], "login_ok", ip)
        return redirect(url_for("admin.dashboard"))

    if not row:
        check_password_hash(_dummy_hash(), password)      # same time cost as a real check
        audit(None, "login_failed_unknown_user", ip)
    elif locked:
        audit(row["id"], "login_blocked_locked", ip)
    else:
        attempts = int(row.get("failed_attempts") or 0) + 1
        patch = {"failed_attempts": attempts}
        if attempts >= MAX_FAILED:
            patch = {"failed_attempts": 0, "locked_until": iso(now + timedelta(minutes=LOCK_MINUTES))}
            audit(row["id"], "account_locked", ip)
        db._request("PATCH", "admin_users", params={"id": f"eq.{row['id']}"}, body=patch,
                    prefer="return=minimal")
        audit(row["id"], "login_failed", ip)
    flash("Invalid credentials, or the account is temporarily locked. Please wait and try again.", "error")
    return redirect(url_for("admin.login"))


@bp.route("/logout", methods=["POST"])
@login_required
def logout():
    if csrf_ok():
        audit(g.user["id"], "logout")
        session.clear()
    return redirect(url_for("admin.login"))


@bp.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password():
    user = g.user
    if request.method == "POST":
        if not csrf_ok():
            flash("Please try again.", "error")
            return redirect(url_for("admin.change_password"))
        current = request.form.get("current", "")[:200]
        new = request.form.get("new", "")[:200]
        again = request.form.get("again", "")[:200]
        rows = _get("admin_users", {"select": "id,username,password_hash",
                                    "id": f"eq.{user['id']}", "limit": "1"})
        problem = None
        if not rows or not check_password_hash(rows[0]["password_hash"], current):
            problem = "Your current password is not correct."
            audit(user["id"], "password_change_failed")
        elif new != again:
            problem = "The two new passwords are not the same."
        elif new == current:
            problem = "The new password must be different from the old one."
        else:
            problem = password_problem(new, rows[0]["username"])
        if problem:
            flash(problem, "error")
            return redirect(url_for("admin.change_password"))
        resp = db._request("PATCH", "admin_users", params={"id": f"eq.{user['id']}"}, prefer="return=minimal",
                           body={"password_hash": make_hash(new), "must_change_password": False,
                                 "failed_attempts": 0})
        if resp is None:
            flash("Could not save the new password. Please try again.", "error")
            return redirect(url_for("admin.change_password"))
        _user_cache.pop(user["id"], None)
        session["csrf"] = secrets.token_urlsafe(32)
        audit(user["id"], "password_changed")
        flash("Password changed successfully.", "ok")
        return redirect(url_for("admin.dashboard"))
    return render("change_password.html", help=PASSWORD_HELP)


# ---------------------------------------------------------------------------
# Dashboard numbers
# ---------------------------------------------------------------------------
_stats_cache = {"t": 0.0, "data": None}
_stats_lock = threading.Lock()

STAT_COLUMNS = ("id,created_at,pilgrim_id,source,category,language,response_ms,answered,"
                "normalized_text,matched_question,query_text")


def _pretty(counter, labels):
    items = sorted(counter.items(), key=lambda kv: -kv[1])
    return {"labels": [labels.get(k, str(k).replace("_", " ").title()) for k, _ in items],
            "values": [v for _, v in items]}


def question_key(row):
    if row.get("matched_question"):
        return "m:" + row["matched_question"]
    return "n:" + (row.get("normalized_text") or "")


def _build_stats():
    now_ist = datetime.now(IST)
    today0 = now_ist.replace(hour=0, minute=0, second=0, microsecond=0)
    since = today0 - timedelta(days=29)
    rows, truncated = _fetch_rows("queries", {
        "select": STAT_COLUMNS, "created_at": "gte." + iso(since), "order": "created_at.desc"}, STATS_ROWS)
    if rows is None:
        return None

    daily, hourly = Counter(), Counter()
    cat, src, lang = Counter(), Counter(), Counter()
    pilgrims, times = set(), []
    answered = today = 0
    top, unanswered = {}, []
    for r in rows:
        dt = parse_ts(r.get("created_at"))
        if not dt:
            continue
        d = dt.astimezone(IST)
        daily[d.date()] += 1
        if d >= today0:
            today += 1
            hourly[d.hour] += 1
        cat[r.get("category") or "unknown"] += 1
        src[r.get("source") or "unknown"] += 1
        lang[r.get("language") or "en"] += 1
        if r.get("pilgrim_id") is not None:
            pilgrims.add(r["pilgrim_id"])
        if isinstance(r.get("response_ms"), int):
            times.append(r["response_ms"])
        if r.get("answered") is not False:
            answered += 1
        elif len(unanswered) < 15:
            unanswered.append(r)
        key = question_key(r)
        if key not in top:                                     # rows are newest first
            top[key] = {"key": key, "count": 0, "last": fmt_ist(dt),
                        "label": (r.get("matched_question") or r.get("query_text") or "")[:120]}
        top[key]["count"] += 1

    n = len(rows)
    ai_used, ai_saved = src.get("ai", 0), src.get("cache", 0)
    codes = codes_for([r.get("pilgrim_id") for r in unanswered])
    days = [(today0 - timedelta(days=29 - i)).date() for i in range(30)]
    return {
        "totals": {
            "all": _count("queries"), "today": today, "pilgrims_total": _count("pilgrims"),
            "pilgrims_30d": len(pilgrims),
            "avg_ms": int(sum(times) / len(times)) if times else None,
            "answered_pct": round(100.0 * answered / n, 1) if n else None,
            "cache_rate": round(100.0 * ai_saved / (ai_saved + ai_used), 1) if (ai_saved + ai_used) else None,
            "ai_saved": ai_saved, "ai_used": ai_used, "rows_used": n},
        "daily": {"labels": [d.strftime("%d %b") for d in days], "values": [daily.get(d, 0) for d in days]},
        "hourly": {"labels": [f"{h}:00" for h in range(now_ist.hour + 1)],
                   "values": [hourly.get(h, 0) for h in range(now_ist.hour + 1)]},
        "category": _pretty(cat, CATEGORY_LABELS),
        "source": _pretty(src, SOURCE_LABELS),
        "language": _pretty(lang, LANG_LABELS),
        "top": sorted(top.values(), key=lambda x: -x["count"])[:15],
        "unanswered": [{"id": r["id"], "t": fmt_ist(r.get("created_at")),
                        "pilgrim": codes.get(r.get("pilgrim_id"), "#?"),
                        "q": (r.get("query_text") or "")[:160]} for r in unanswered],
        "truncated": truncated,
        "updated": now_ist.strftime("%I:%M:%S %p"),
    }


def compute_stats():
    if _stats_cache["data"] and time.time() - _stats_cache["t"] < 8:
        return _stats_cache["data"]
    with _stats_lock:
        if _stats_cache["data"] and time.time() - _stats_cache["t"] < 8:
            return _stats_cache["data"]
        data = _build_stats()
        if data:
            _stats_cache.update(t=time.time(), data=data)
        return data or _stats_cache["data"]


@bp.route("/dashboard")
@login_required
def dashboard():
    return render("dashboard.html", charts=True, active="dashboard")


@bp.route("/api/stats")
@login_required
def api_stats():
    data = compute_stats()
    if data is None:
        return jsonify(error="database"), 503
    return jsonify(data)


@bp.route("/api/recent")
@login_required
def api_recent():
    after = request.args.get("after", type=int) or 0
    params = {"select": "id,created_at,pilgrim_id,query_text,source,answered",
              "order": "id.desc", "limit": "25" if after <= 0 else "50"}
    if after > 0:
        params["id"] = f"gt.{after}"
    rows = _get("queries", params)
    if rows is None:
        return jsonify(error="database"), 503
    codes = codes_for([r.get("pilgrim_id") for r in rows])
    out = [{"id": r["id"], "t": fmt_ist(r.get("created_at"), seconds=True),
            "pilgrim": codes.get(r.get("pilgrim_id"), "#?"), "q": (r.get("query_text") or "")[:200],
            "source": r.get("source") or "", "answered": r.get("answered") is not False} for r in rows]
    return jsonify(rows=out, max_id=max([r["id"] for r in rows], default=after))


# ---------------------------------------------------------------------------
# Questions list (filters) + CSV
# ---------------------------------------------------------------------------
LIST_COLUMNS = ("id,created_at,pilgrim_id,query_text,normalized_text,matched_question,"
                "source,category,language,response_ms,answered")


def _query_filters():
    a = request.args
    f = {"date_from": a.get("date_from", "").strip()[:10], "date_to": a.get("date_to", "").strip()[:10],
         "category": a.get("category", "").strip(), "language": a.get("language", "").strip(),
         "source": a.get("source", "").strip(), "q": a.get("q", "").strip()[:80]}
    d1, d2 = parse_date(f["date_from"]), parse_date(f["date_to"])
    if not d1:
        f["date_from"] = ""
    if not d2:
        f["date_to"] = ""
    if f["category"] not in CATEGORIES:
        f["category"] = ""
    if f["language"] not in LANGS:
        f["language"] = ""
    if f["source"] not in SOURCES:
        f["source"] = ""
    params = {}
    for col in ("category", "language", "source"):
        if f[col]:
            params[col] = "eq." + f[col]
    term = re.sub(r"[*%,()]", " ", f["q"]).strip()
    if term:
        params["query_text"] = "ilike.*" + term + "*"
    conds = []
    if d1:
        conds.append("created_at.gte." + ist_midnight_utc(d1))
    if d2:
        conds.append("created_at.lt." + ist_midnight_utc(d2 + timedelta(days=1)))
    if conds:
        params["and"] = "(" + ",".join(conds) + ")"
    return f, params, {k: v for k, v in f.items() if v}


def _decorate(rows):
    codes = codes_for([r.get("pilgrim_id") for r in rows])
    out = []
    for r in rows:
        code = codes.get(r.get("pilgrim_id"), "#?")
        out.append({"id": r["id"], "t": fmt_ist(r.get("created_at")), "code": code,
                    "num": code.lstrip("#"), "text": r.get("query_text") or "", "qkey": question_key(r),
                    "source": r.get("source") or "", "category": r.get("category") or "",
                    "language": r.get("language") or "", "ms": r.get("response_ms"),
                    "answered": r.get("answered") is not False, "reply": r.get("reply_text") or ""})
    return out


@bp.route("/queries")
@login_required
def queries():
    f, params, base_args = _query_filters()
    page = min(max(request.args.get("page", 1, type=int) or 1, 1), 2000)
    total = _count("queries", params)
    rows = _get("queries", {**params, "select": LIST_COLUMNS, "order": "id.desc",
                            "limit": str(PAGE_SIZE), "offset": str((page - 1) * PAGE_SIZE)})
    if rows is None:
        return render("message.html", title="Please wait", text="Could not load questions. Try again."), 503
    pages = max(1, -(-(total or 0) // PAGE_SIZE))
    return render("queries.html", active="queries", f=f, base_args=base_args, rows=_decorate(rows),
                  total=total, page=page, pages=pages, categories=CATEGORIES, sources=SOURCES,
                  langs=LANGS, labels={"c": CATEGORY_LABELS, "s": SOURCE_LABELS, "l": LANG_LABELS})


def _csv_safe(v):
    s = "" if v is None else str(v)
    return "'" + s if s[:1] in ("=", "+", "-", "@", "\t", "\r") else s


@bp.route("/export.csv")
@login_required
def export_csv():
    f, params, _ = _query_filters()
    rows, truncated = _fetch_rows("queries", {**params, "select": LIST_COLUMNS + ",reply_text",
                                               "order": "id.desc"}, CSV_MAX_ROWS)
    if rows is None:
        return render("message.html", title="Please wait", text="Could not build the file. Try again."), 503
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["id", "time_ist", "pilgrim", "language", "source", "category", "answered",
                "response_ms", "question", "reply"])
    for r in _decorate(rows):
        w.writerow([r["id"], r["t"], r["code"], r["language"], r["source"], r["category"],
                    "yes" if r["answered"] else "no", r["ms"] if r["ms"] is not None else "",
                    _csv_safe(r["text"]), _csv_safe(r["reply"])])
    audit(g.user["id"], "export_csv")
    resp = make_response("\ufeff" + buf.getvalue())
    resp.headers["Content-Type"] = "text/csv; charset=utf-8"
    resp.headers["Content-Disposition"] = "attachment; filename=sudarshan_queries_%s.csv" % datetime.now(IST).strftime("%Y%m%d")
    return resp


# ---------------------------------------------------------------------------
# Question detail and pilgrim detail
# ---------------------------------------------------------------------------
@bp.route("/question")
@login_required
def question():
    key = request.args.get("k", "")[:400]
    col = {"m:": "matched_question", "n:": "normalized_text"}.get(key[:2])
    value = key[2:]
    if not col or not value:
        abort(404)
    params = {col: "eq." + value}
    total = _count("queries", params)
    rows = _get("queries", {**params, "select": LIST_COLUMNS + ",reply_text", "order": "id.desc", "limit": "300"})
    if not rows:
        return render("message.html", title="Not found", text="No records found for this question."), 404
    items = _decorate(rows)
    per_day = Counter()
    for r in rows:
        dt = parse_ts(r.get("created_at"))
        if dt:
            per_day[dt.astimezone(IST).date()] += 1
    days = sorted(per_day)
    first = parse_ts(rows[-1].get("created_at")) if total is not None and total <= len(rows) else None
    return render("question.html", charts=True, active="queries",
                  title_text=(rows[0].get("matched_question") or rows[0].get("query_text") or value)[:200],
                  total=total, last=fmt_ist(rows[0].get("created_at")), first=fmt_ist(first) if first else None,
                  shown=len(rows), rows=items,
                  trend={"labels": [d.strftime("%d %b") for d in days], "values": [per_day[d] for d in days]})


@bp.route("/pilgrim/<code>")
@login_required
def pilgrim(code):
    digits = code.lstrip("#")
    if not re.fullmatch(r"\d{3,9}", digits):
        abort(404)
    prow = _get("pilgrims", {"select": "id,pilgrim_code,first_seen,last_seen,message_count",
                             "pilgrim_code": "eq.#" + digits, "limit": "1"})
    if not prow:
        return render("message.html", title="Not found", text="No such pilgrim code."), 404
    p = prow[0]
    rows = _get("queries", {"select": LIST_COLUMNS + ",reply_text", "pilgrim_id": f"eq.{p['id']}",
                            "order": "id.desc", "limit": "200"}) or []
    return render("pilgrim.html", active="queries", p=p, first=fmt_ist(p.get("first_seen")),
                  last=fmt_ist(p.get("last_seen")), rows=_decorate(rows))


# ---------------------------------------------------------------------------
# Styles and script (served from /admin/static/...)
# ---------------------------------------------------------------------------
CSS = r"""
:root{--maroon:#6E1423;--maroon2:#8E2236;--saffron:#E8890C;--cream:#FFF7EA;--ink:#2B1B17;--line:#EBD9BF;--ok:#2E7D32;--bad:#B3261E}
*{box-sizing:border-box}
body{margin:0;font-family:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;background:var(--cream);color:var(--ink);line-height:1.45}
a{color:var(--maroon2)}
.top{background:var(--maroon);color:#fff;border-bottom:4px solid var(--saffron);padding:10px 16px;display:flex;flex-wrap:wrap;gap:10px;align-items:center}
.top h2{margin:0;font-size:1.05rem;flex:1 1 auto}
.top nav{display:flex;gap:6px;flex-wrap:wrap;align-items:center}
.top a,.top button{color:#fff;text-decoration:none;padding:6px 12px;border-radius:6px;background:transparent;border:1px solid rgba(255,255,255,.35);font-size:.9rem;cursor:pointer}
.top a.on,.top a:hover,.top button:hover{background:var(--maroon2)}
.top form{margin:0}
.wrap{max-width:1180px;margin:0 auto;padding:16px}
h1{font-size:1.35rem;margin:6px 0 12px;color:var(--maroon)}
h3{margin:0 0 8px;font-size:1rem;color:var(--maroon)}
.bar{display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;margin:8px 0 14px}
.card,.panel{background:#fff;border:1px solid var(--line);border-radius:10px;padding:12px}
.card .k{font-size:.78rem;color:#7a6659;text-transform:uppercase;letter-spacing:.03em}
.card .v{font-size:1.6rem;font-weight:700;color:var(--maroon)}
.card .s{font-size:.78rem;color:#7a6659}
.grid2{display:grid;grid-template-columns:repeat(auto-fit,minmax(310px,1fr));gap:12px;margin-bottom:12px}
.chartbox{position:relative;height:230px}
.scroll{overflow-x:auto}
table{width:100%;border-collapse:collapse;font-size:.88rem}
th,td{text-align:left;padding:7px 8px;border-bottom:1px solid var(--line);vertical-align:top}
th{font-size:.75rem;text-transform:uppercase;color:#7a6659;white-space:nowrap}
td.q{max-width:420px;word-break:break-word}
.pill{display:inline-block;padding:1px 8px;border-radius:99px;font-size:.75rem;background:#eee;color:#444}
.s-ai{background:#fde7c4;color:#7a4300}.s-cache{background:#d9f0dc;color:#1b5e20}.s-direct{background:#dbe9fb;color:#0d3c78}
.s-guardrail{background:#f3dcf5;color:#6a1b7a}.s-fallback{background:#fadbd8;color:#a1241b}.s-menu,.s-greeting{background:#ececec}
.live{display:inline-flex;align-items:center;gap:6px;font-size:.85rem}
.live i{width:10px;height:10px;border-radius:50%;background:#aaa;display:inline-block}
.live.on i{background:var(--ok);animation:p 1.4s infinite}.live.off i{background:var(--bad)}
@keyframes p{0%{box-shadow:0 0 0 0 rgba(46,125,50,.5)}100%{box-shadow:0 0 0 8px rgba(46,125,50,0)}}
tr.fresh td{animation:f 3s ease-out}
@keyframes f{0%{background:#ffe3a3}100%{background:transparent}}
.msg{padding:9px 12px;border-radius:8px;margin:8px 0;font-size:.92rem}
.msg.error{background:#fde8e6;color:#8a1c14;border:1px solid #f4b9b3}
.msg.ok{background:#e3f4e5;color:#1b5e20;border:1px solid #b5ddb9}
.notice{background:#fff3cd;border:1px solid #f0d98a;padding:9px 12px;border-radius:8px}
form.box{max-width:420px;margin:30px auto;background:#fff;border:1px solid var(--line);border-radius:12px;padding:20px}
label{display:block;margin:10px 0 4px;font-size:.88rem;font-weight:600}
input,select{width:100%;padding:9px 10px;border:1px solid #cdb995;border-radius:7px;font-size:1rem;background:#fff}
button.go,a.go{display:inline-block;margin-top:14px;background:var(--maroon);color:#fff;border:0;border-radius:8px;padding:10px 18px;font-size:1rem;cursor:pointer;text-decoration:none}
button.go:hover,a.go:hover{background:var(--maroon2)}
.filters{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:8px;align-items:end}
.filters button.go{margin:0}
.pager{display:flex;gap:10px;align-items:center;justify-content:center;margin:12px 0}
details summary{cursor:pointer;color:var(--maroon2);font-size:.82rem}
details pre{white-space:pre-wrap;font-family:inherit;margin:6px 0 0;background:#fffaf0;border:1px solid var(--line);padding:8px;border-radius:6px;max-width:520px}
.muted{color:#7a6659;font-size:.85rem}
@media(max-width:600px){.card .v{font-size:1.3rem}.wrap{padding:10px}}
"""

JS = r"""
(function () {
  "use strict";
  var PAL = ["#B8460E", "#E8890C", "#6E1423", "#D9A441", "#5E7D3A", "#3F6C8C", "#8E5A9B", "#999999"];
  var charts = {}, timer = null, lastId = 0, firstFeed = true, busy = false;
  function $(id) { return document.getElementById(id); }
  function num(n) { return (n === null || n === undefined) ? "–" : Number(n).toLocaleString("en-IN"); }
  function el(tag, cls, text) {
    var e = document.createElement(tag);
    if (cls) { e.className = cls; }
    if (text !== undefined && text !== null) { e.textContent = String(text); }
    return e;
  }
  function chart(id, type, labels, values) {
    if (typeof Chart === "undefined" || !$(id)) { var n = $("chartNote"); if (n) { n.hidden = false; } return; }
    if (charts[id]) {
      charts[id].data.labels = labels; charts[id].data.datasets[0].data = values; charts[id].update("none"); return;
    }
    var ds = { data: values };
    if (type === "line") { ds.borderColor = "#6E1423"; ds.backgroundColor = "rgba(232,137,12,.25)"; ds.fill = true; ds.tension = .25; }
    else if (type === "bar") { ds.backgroundColor = "#E8890C"; }
    else { ds.backgroundColor = PAL; }
    charts[id] = new Chart($(id), {
      type: type, data: { labels: labels, datasets: [ds] },
      options: { responsive: true, maintainAspectRatio: false, animation: false,
        plugins: { legend: { display: type === "doughnut", position: "bottom" } },
        scales: type === "doughnut" ? {} : { y: { beginAtZero: true, ticks: { precision: 0 } } } }
    });
  }
  function setLive(ok, text) {
    var d = $("live"); if (!d) { return; }
    d.className = "live " + (ok ? "on" : "off"); d.querySelector("span").textContent = text;
  }
  function expired() {
    if (timer) { clearInterval(timer); timer = null; }
    setLive(false, "Logged out");
    var l = $("expired"); if (l) { l.hidden = false; }
  }
  function api(url) {
    return fetch(url, { credentials: "same-origin", cache: "no-store", headers: { "Accept": "application/json" } })
      .then(function (r) {
        if (r.status === 401) { expired(); throw new Error("auth"); }
        if (!r.ok) { throw new Error("http"); }
        return r.json();
      });
  }
  function fill(id, rows, build, cols, emptyText) {
    var body = $(id); if (!body) { return; }
    body.textContent = "";
    if (!rows.length) {
      var tr = el("tr"), td = el("td", "muted", emptyText); td.colSpan = cols; tr.appendChild(td); body.appendChild(tr); return;
    }
    rows.forEach(function (r) { body.appendChild(build(r)); });
  }
  function pilgrimLink(code) {
    var a = el("a", null, code); a.href = "/admin/pilgrim/" + encodeURIComponent(String(code).replace("#", "")); return a;
  }
  function feedRow(r) {
    var tr = el("tr");
    tr.appendChild(el("td", null, r.t));
    var c = el("td"); c.appendChild(pilgrimLink(r.pilgrim)); tr.appendChild(c);
    tr.appendChild(el("td", "q", r.q));
    var s = el("td"); s.appendChild(el("span", "pill s-" + String(r.source).replace(/[^a-z]/g, ""), r.source)); tr.appendChild(s);
    tr.appendChild(el("td", null, r.answered ? "Yes" : "No"));
    return tr;
  }
  function renderStats(d) {
    var t = d.totals;
    $("cTotal").textContent = num(t.all); $("cToday").textContent = num(t.today);
    $("cPilgrims").textContent = num(t.pilgrims_total);
    $("cMs").textContent = t.avg_ms === null ? "–" : (t.avg_ms >= 1000 ? (t.avg_ms / 1000).toFixed(1) + " s" : t.avg_ms + " ms");
    $("cAnswered").textContent = t.answered_pct === null ? "–" : t.answered_pct + "%";
    $("cCache").textContent = t.cache_rate === null ? "–" : t.cache_rate + "%";
    $("cSaved").textContent = num(t.ai_saved) + " AI calls saved";
    chart("chDaily", "line", d.daily.labels, d.daily.values);
    chart("chHourly", "bar", d.hourly.labels, d.hourly.values);
    chart("chCategory", "bar", d.category.labels, d.category.values);
    chart("chSource", "doughnut", d.source.labels, d.source.values);
    chart("chLang", "doughnut", d.language.labels, d.language.values);
    fill("topBody", d.top, function (r) {
      var tr = el("tr"), c = el("td", "q"), a = el("a", null, r.label || "(empty)");
      a.href = "/admin/question?k=" + encodeURIComponent(r.key); c.appendChild(a); tr.appendChild(c);
      tr.appendChild(el("td", null, r.count)); tr.appendChild(el("td", null, r.last)); return tr;
    }, 3, "No questions yet.");
    fill("unBody", d.unanswered, function (r) {
      var tr = el("tr"); tr.appendChild(el("td", null, r.t));
      var c = el("td"); c.appendChild(pilgrimLink(r.pilgrim)); tr.appendChild(c);
      tr.appendChild(el("td", "q", r.q)); return tr;
    }, 3, "Nothing unanswered. 🙏");
    var note = $("trunc"); if (note) { note.hidden = !d.truncated; }
    $("updated").textContent = "Updated " + d.updated;
  }
  function pollFeed() {
    return api("/admin/api/recent?after=" + lastId).then(function (d) {
      var body = $("feedBody"); if (!body) { return; }
      if (firstFeed) { body.textContent = ""; }
      d.rows.slice().reverse().forEach(function (r) {
        var tr = feedRow(r); if (!firstFeed) { tr.className = "fresh"; }
        body.insertBefore(tr, body.firstChild);
      });
      while (body.children.length > 40) { body.removeChild(body.lastChild); }
      if (d.max_id > lastId) { lastId = d.max_id; }
      firstFeed = false;
      $("feedEmpty").hidden = body.children.length > 0;
    });
  }
  function tick() {
    if (busy || document.hidden) { return; }
    busy = true;
    Promise.all([api("/admin/api/stats").then(renderStats), pollFeed()])
      .then(function () { setLive(true, "Live"); })
      .catch(function (e) { if (e.message !== "auth") { setLive(false, "Reconnecting…"); } })
      .then(function () { busy = false; });
  }
  if ($("cTotal")) { tick(); timer = setInterval(tick, 5000); }
  var td = $("trendData");
  if (td) { try { var t = JSON.parse(td.textContent); chart("chTrend", "line", t.labels, t.values); } catch (e) { /* ignore */ } }
})();
"""


@bp.route("/static/admin.css")
def asset_css():
    r = make_response(CSS)
    r.headers["Content-Type"] = "text/css; charset=utf-8"
    return r


@bp.route("/static/admin.js")
def asset_js():
    r = make_response(JS)
    r.headers["Content-Type"] = "application/javascript; charset=utf-8"
    return r


# ---------------------------------------------------------------------------
# Page templates (Jinja2; everything is auto-escaped)
# ---------------------------------------------------------------------------
TEMPLATES = {
"base.html": r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<title>{% block title %}Admin{% endblock %} – Sudarshan AI – TTD Admin</title>
<link rel="stylesheet" href="{{ url_for('admin.asset_css') }}">
</head><body>
{% if user %}
<header class="top"><h2>🛕 Sudarshan AI – TTD Admin</h2>
<nav>
<a href="{{ url_for('admin.dashboard') }}" class="{{ 'on' if active == 'dashboard' }}">Dashboard</a>
<a href="{{ url_for('admin.queries') }}" class="{{ 'on' if active == 'queries' }}">Questions</a>
<a href="{{ url_for('admin.change_password') }}">Change password</a>
<form method="post" action="{{ url_for('admin.logout') }}"><input type="hidden" name="csrf_token" value="{{ csrf() }}"><button type="submit">Log out</button></form>
</nav></header>
{% else %}
<header class="top"><h2>🛕 Sudarshan AI – TTD Admin</h2></header>
{% endif %}
<main class="wrap">
{% for cat, text in messages %}<div class="msg {{ cat }}">{{ text }}</div>{% endfor %}
{% block content %}{% endblock %}
</main>
{% if charts %}<script src="{{ chartjs }}" defer></script>{% endif %}
<script src="{{ url_for('admin.asset_js') }}" defer></script>
</body></html>""",

"message.html": r"""{% extends "base.html" %}
{% block title %}{{ title }}{% endblock %}
{% block content %}<h1>{{ title }}</h1><p>{{ text }}</p><p><a href="{{ url_for('admin.dashboard') }}">Back to dashboard</a></p>{% endblock %}""",

"login.html": r"""{% extends "base.html" %}
{% block title %}Login{% endblock %}
{% block content %}
<form class="box" method="post" action="{{ url_for('admin.login') }}" autocomplete="on">
<h1>Admin login</h1>
<input type="hidden" name="csrf_token" value="{{ csrf() }}">
<label for="u">Username</label><input id="u" name="username" autocomplete="username" required maxlength="60" autofocus>
<label for="p">Password</label><input id="p" name="password" type="password" autocomplete="current-password" required maxlength="200">
<button class="go" type="submit">Log in</button>
</form>{% endblock %}""",

"change_password.html": r"""{% extends "base.html" %}
{% block title %}Change password{% endblock %}
{% block content %}
<form class="box" method="post" action="{{ url_for('admin.change_password') }}">
<h1>Change password</h1>
{% if user and user.must_change_password %}<div class="notice">You must choose a new password before you continue.</div>{% endif %}
<p class="muted">{{ help }}</p>
<input type="hidden" name="csrf_token" value="{{ csrf() }}">
<label for="c">Current password</label><input id="c" name="current" type="password" autocomplete="current-password" required>
<label for="n">New password</label><input id="n" name="new" type="password" autocomplete="new-password" required>
<label for="a">New password again</label><input id="a" name="again" type="password" autocomplete="new-password" required>
<button class="go" type="submit">Save new password</button>
</form>{% endblock %}""",

"dashboard.html": r"""{% extends "base.html" %}
{% block title %}Dashboard{% endblock %}
{% block content %}
<div class="bar"><h1>Live dashboard</h1>
<div><span id="live" class="live off"><i></i><span>Connecting…</span></span> <span id="updated" class="muted"></span></div></div>
<p id="expired" class="notice" hidden><a href="{{ url_for('admin.login') }}">You were logged out (30 minutes without activity). Click here to log in again.</a></p>
<p id="chartNote" class="notice" hidden>Charts could not load (the chart library is blocked). The numbers and tables still work.</p>
<section class="cards">
<div class="card"><div class="k">Total questions</div><div class="v" id="cTotal">–</div></div>
<div class="card"><div class="k">Today</div><div class="v" id="cToday">–</div></div>
<div class="card"><div class="k">Pilgrims</div><div class="v" id="cPilgrims">–</div></div>
<div class="card"><div class="k">Avg reply time</div><div class="v" id="cMs">–</div></div>
<div class="card"><div class="k">Answered</div><div class="v" id="cAnswered">–</div></div>
<div class="card"><div class="k">Cache hit rate</div><div class="v" id="cCache">–</div><div class="s" id="cSaved"></div></div>
</section>
<p class="muted" id="trunc" hidden>Charts and rates use the newest 5,000 questions from the last 30 days.</p>
<section class="grid2">
<div class="panel"><h3>Questions per day (last 30 days)</h3><div class="chartbox"><canvas id="chDaily"></canvas></div></div>
<div class="panel"><h3>Questions per hour (today)</h3><div class="chartbox"><canvas id="chHourly"></canvas></div></div>
<div class="panel"><h3>By category</h3><div class="chartbox"><canvas id="chCategory"></canvas></div></div>
<div class="panel"><h3>By answer source</h3><div class="chartbox"><canvas id="chSource"></canvas></div></div>
<div class="panel"><h3>By language</h3><div class="chartbox"><canvas id="chLang"></canvas></div></div>
</section>
<section class="grid2">
<div class="panel"><h3>Top questions (click to open)</h3><div class="scroll"><table>
<thead><tr><th>Question</th><th>Times</th><th>Last asked</th></tr></thead><tbody id="topBody"></tbody></table></div></div>
<div class="panel"><h3>Unanswered questions (need improvement)</h3><div class="scroll"><table>
<thead><tr><th>Time</th><th>Pilgrim</th><th>Question</th></tr></thead><tbody id="unBody"></tbody></table></div></div>
</section>
<section class="panel"><h3>Live feed</h3><div class="scroll"><table>
<thead><tr><th>Time</th><th>Pilgrim</th><th>Question</th><th>Source</th><th>Answered</th></tr></thead><tbody id="feedBody"></tbody></table></div>
<p id="feedEmpty" class="muted" hidden>No questions yet.</p></section>
{% endblock %}""",

"queries.html": r"""{% extends "base.html" %}
{% block title %}Questions{% endblock %}
{% block content %}
<div class="bar"><h1>Questions</h1><a class="go" href="{{ url_for('admin.export_csv', **base_args) }}">⬇ Download CSV</a></div>
<form method="get" class="panel filters">
<div><label>From date</label><input type="date" name="date_from" value="{{ f.date_from }}"></div>
<div><label>To date</label><input type="date" name="date_to" value="{{ f.date_to }}"></div>
<div><label>Category</label><select name="category"><option value="">All</option>{% for c in categories %}<option value="{{ c }}" {{ 'selected' if f.category == c }}>{{ labels.c.get(c, c|capitalize) }}</option>{% endfor %}</select></div>
<div><label>Language</label><select name="language"><option value="">All</option>{% for l in langs %}<option value="{{ l }}" {{ 'selected' if f.language == l }}>{{ labels.l.get(l, l) }}</option>{% endfor %}</select></div>
<div><label>Source</label><select name="source"><option value="">All</option>{% for s in sources %}<option value="{{ s }}" {{ 'selected' if f.source == s }}>{{ labels.s.get(s, s) }}</option>{% endfor %}</select></div>
<div><label>Search text</label><input name="q" value="{{ f.q }}" maxlength="80"></div>
<div><button class="go" type="submit">Filter</button></div>
</form>
<p class="muted">{{ total if total is not none else '?' }} questions found. Times are in India time (IST).</p>
<div class="panel scroll"><table>
<thead><tr><th>Time</th><th>Pilgrim</th><th>Question</th><th>Source</th><th>Category</th><th>Lang</th><th>Answered</th><th>ms</th></tr></thead><tbody>
{% for r in rows %}<tr>
<td>{{ r.t }}</td><td><a href="{{ url_for('admin.pilgrim', code=r.num) }}">{{ r.code }}</a></td>
<td class="q"><a href="{{ url_for('admin.question', k=r.qkey) }}">{{ r.text or '(empty)' }}</a></td>
<td><span class="pill s-{{ r.source }}">{{ r.source }}</span></td><td>{{ r.category }}</td><td>{{ r.language }}</td>
<td>{{ 'Yes' if r.answered else 'No' }}</td><td>{{ r.ms if r.ms is not none else '' }}</td></tr>
{% else %}<tr><td colspan="8" class="muted">No questions match.</td></tr>{% endfor %}
</tbody></table></div>
<div class="pager">
{% if page > 1 %}<a href="{{ url_for('admin.queries', page=page-1, **base_args) }}">← Newer</a>{% endif %}
<span>Page {{ page }} of {{ pages }}</span>
{% if page < pages %}<a href="{{ url_for('admin.queries', page=page+1, **base_args) }}">Older →</a>{% endif %}
</div>{% endblock %}""",

"question.html": r"""{% extends "base.html" %}
{% block title %}Question{% endblock %}
{% block content %}
<p><a href="{{ url_for('admin.queries') }}">← All questions</a></p>
<h1>{{ title_text }}</h1>
<section class="cards">
<div class="card"><div class="k">Times asked</div><div class="v">{{ total if total is not none else shown }}</div></div>
<div class="card"><div class="k">Last asked</div><div class="s">{{ last }}</div></div>
{% if first %}<div class="card"><div class="k">First asked</div><div class="s">{{ first }}</div></div>{% endif %}
</section>
<div class="panel"><h3>Trend</h3><div class="chartbox"><canvas id="chTrend"></canvas></div>
<script type="application/json" id="trendData">{{ trend|tojson }}</script></div>
<div class="panel scroll" style="margin-top:12px"><h3>Every time it was asked{% if total and total > shown %} (newest {{ shown }}){% endif %}</h3><table>
<thead><tr><th>Time</th><th>Pilgrim</th><th>Lang</th><th>Source</th><th>ms</th><th>Reply shown</th></tr></thead><tbody>
{% for r in rows %}<tr><td>{{ r.t }}</td><td><a href="{{ url_for('admin.pilgrim', code=r.num) }}">{{ r.code }}</a></td>
<td>{{ r.language }}</td><td><span class="pill s-{{ r.source }}">{{ r.source }}</span></td><td>{{ r.ms if r.ms is not none else '' }}</td>
<td><details><summary>Show reply</summary><pre>{{ r.reply }}</pre></details></td></tr>{% endfor %}
</tbody></table></div>{% endblock %}""",

"pilgrim.html": r"""{% extends "base.html" %}
{% block title %}Pilgrim {{ p.pilgrim_code }}{% endblock %}
{% block content %}
<p><a href="{{ url_for('admin.queries') }}">← All questions</a></p>
<h1>Pilgrim {{ p.pilgrim_code }}</h1>
<section class="cards">
<div class="card"><div class="k">Messages</div><div class="v">{{ p.message_count }}</div></div>
<div class="card"><div class="k">First seen</div><div class="s">{{ first }}</div></div>
<div class="card"><div class="k">Last seen</div><div class="s">{{ last }}</div></div>
</section>
<div class="panel scroll"><h3>Questions from this pilgrim (newest 200)</h3><table>
<thead><tr><th>Time</th><th>Question</th><th>Source</th><th>Answered</th><th>Reply shown</th></tr></thead><tbody>
{% for r in rows %}<tr><td>{{ r.t }}</td><td class="q"><a href="{{ url_for('admin.question', k=r.qkey) }}">{{ r.text or '(empty)' }}</a></td>
<td><span class="pill s-{{ r.source }}">{{ r.source }}</span></td><td>{{ 'Yes' if r.answered else 'No' }}</td>
<td><details><summary>Show reply</summary><pre>{{ r.reply }}</pre></details></td></tr>
{% else %}<tr><td colspan="5" class="muted">No questions.</td></tr>{% endfor %}
</tbody></table></div>{% endblock %}""",
}

_env = Environment(loader=DictLoader(TEMPLATES), autoescape=True)
_env.globals["url_for"] = url_for
_env.globals["csrf"] = csrf_token


# ---------------------------------------------------------------------------
# Connect to the Flask app (called once from app.py)
# ---------------------------------------------------------------------------
def register(app):
    if not ADMIN_ENABLED:
        log.warning("Admin website is OFF. Add SECRET_KEY (32+ random characters) in Render > Environment.")
    else:
        app.secret_key = SECRET_KEY
    app.config.update(
        SESSION_COOKIE_NAME="sudarshan_admin",
        SESSION_COOKIE_PATH="/admin",
        SESSION_COOKIE_SECURE=not os.environ.get("ADMIN_ALLOW_HTTP"),
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Strict",
    )
    # Render talks to us through a proxy: trust its scheme/host headers.
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    app.register_blueprint(bp)
