# -*- coding: utf-8 -*-
"""
notices.py
----------
LIVE NOTICES typed by TTD staff in the admin panel (Notices page), for things that
change every day: SSD token timings, Rs.300 ticket availability, VIP break darshan, crowd
status, one-day rules (for example "no VIP tickets on Wednesday").

When a pilgrim asks about one of these topics WITH a time word (today, tomorrow, when,
timing, ...), the bot answers from the notices valid for those dates. If staff have not
posted anything, the bot says so honestly and points to tirumala.org. No AI is used, so
the answer can never be invented.

Admin changes reach the bot within about 30 seconds.
"""

import re
import time
import logging
from collections import OrderedDict
from datetime import datetime, timedelta, timezone

import db

log = logging.getLogger("sudarshan-ai.notices")

IST = timezone(timedelta(hours=5, minutes=30))

TOPICS = OrderedDict([
    ("ssd_tokens", {
        "en": "SSD Tokens (free darshan tokens)", "te": "SSD టోకెన్లు (ఉచిత దర్శన టోకెన్లు)",
        "kw": ["ssd", "slotted sarva", "token", "టోకెన్"]}),
    ("special_entry_300", {
        "en": "₹300 Special Entry Darshan tickets", "te": "₹300 స్పెషల్ ఎంట్రీ దర్శన టికెట్లు",
        "kw": ["300", "special entry", "స్పెషల్ ఎంట్రీ"]}),
    ("vip_break", {
        "en": "VIP Break Darshan", "te": "VIP బ్రేక్ దర్శనం",
        "kw": ["vip", "break darshan", "విఐపి", "వీఐపీ"]}),
    ("darshan_status", {
        "en": "Darshan crowd / waiting time", "te": "దర్శనం రద్దీ / వేచి ఉండే సమయం",
        "kw": ["crowd", "rush", "queue", "waiting time", "wait time", "రద్దీ", "క్యూ"]}),
    ("general", {"en": "TTD announcement", "te": "TTD ప్రకటన", "kw": []}),
])

_TIME_EN = {"today", "tomorrow", "tonight", "now", "timing", "timings", "time", "when", "open", "opens",
            "opening", "start", "starts", "release", "released", "available", "availability", "date",
            "status", "day", "current", "currently"}
_TIME_TE = ["ఈరోజు", "రేపు", "ఇప్పుడు", "ఎప్పుడు", "సమయం", "టైమ్", "తేదీ", "అందుబాటు", "ఈ రోజు"]
_WEEKDAYS_EN = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
_WEEKDAYS_TE = ["సోమవారం", "మంగళవారం", "బుధవారం", "గురువారం", "శుక్రవారం", "శనివారం", "ఆదివారం"]

_cache = {"t": 0.0, "rows": None}


def ist_today():
    return datetime.now(IST).date()


def invalidate():
    _cache["t"] = 0.0


def _parse(s):
    if not s:
        return None
    try:
        s = str(s).replace("Z", "+00:00")
        m = re.match(r"(.*?\.)(\d+)(.*)$", s)
        if m:
            s = m.group(1) + (m.group(2) + "000000")[:6] + m.group(3)
        d = datetime.fromisoformat(s)
        return d if d.tzinfo else d.replace(tzinfo=timezone.utc)
    except Exception:  # noqa: BLE001
        return None


def fetch_active():
    """Active notices that have not expired. Cached for 30 seconds. None = database down."""
    if _cache["rows"] is not None and time.time() - _cache["t"] < 30:
        return _cache["rows"]
    rows = db._json(db._request("GET", "notices", timeout=3, params={
        "select": "id,topic,message_en,message_te,valid_from,valid_to,weekday,updated_at",
        "active": "eq.true", "valid_to": f"gte.{ist_today().isoformat()}",
        "order": "id.asc", "limit": "500"}))
    if rows is None:
        return _cache["rows"]            # stale copy (or None) if the database is down
    _cache.update(t=time.time(), rows=rows)
    return rows


def _has(text, kw):
    if re.fullmatch(r"[a-z0-9 ]+", kw):
        return re.search(r"\b" + re.escape(kw) + r"\b", text) is not None
    return kw in text


def detect_topic(text):
    t = (text or "").lower()
    for key, info in TOPICS.items():
        if any(_has(t, k) for k in info["kw"]):
            return key
    return None


def _time_hint(t):
    words = set(re.findall(r"[a-z]+", t))
    return bool(words & _TIME_EN) or any(w in t for w in _TIME_TE) or \
        any(d in t for d in _WEEKDAYS_EN + _WEEKDAYS_TE)


def _target_days(t):
    today = ist_today()
    for i, name in enumerate(_WEEKDAYS_EN):
        if re.search(r"\b" + name + r"\b", t):
            return [today + timedelta(days=(i - today.weekday()) % 7)]
    for i, name in enumerate(_WEEKDAYS_TE):
        if name in t:
            return [today + timedelta(days=(i - today.weekday()) % 7)]
    if "tomorrow" in t or "రేపు" in t:
        return [today + timedelta(days=1)]
    if re.search(r"\btoday\b|\btonight\b|\bnow\b", t) or "ఈరోజు" in t or "ఈ రోజు" in t or "ఇప్పుడు" in t:
        return [today]
    return [today, today + timedelta(days=1)]


def _applies(n, d):
    vf, vt = str(n.get("valid_from"))[:10], str(n.get("valid_to"))[:10]
    if not (vf <= d.isoformat() <= vt):
        return False
    wd = n.get("weekday")
    return wd is None or int(wd) == d.weekday()


def _day_label(d, telugu):
    today = ist_today()
    base = d.strftime("%a, %d %b")
    if d == today:
        return ("ఈరోజు" if telugu else "Today") + f" ({base})"
    if d == today + timedelta(days=1):
        return ("రేపు" if telugu else "Tomorrow") + f" ({base})"
    return d.strftime("%A, %d %b")


def find_reply(text, telugu=False):
    """Returns {"reply", "topic"} when the message is a live-information question, else None."""
    t = (text or "").lower()
    topic = detect_topic(t)
    if not topic or not _time_hint(t):
        return None
    rows = fetch_active()
    if rows is None:
        return None                      # database down: fall back to the normal answer

    info = TOPICS[topic]
    days = _target_days(t)
    lines = [f"🔔 *{'లైవ్ అప్‌డేట్' if telugu else 'Live update'}: {info['te' if telugu else 'en']}*"]
    newest, found_any = None, False
    for d in days:
        matching = [n for n in rows if n.get("topic") == topic and _applies(n, d)]
        lines.append("")
        lines.append(f"📅 *{_day_label(d, telugu)}*")
        if not matching:
            lines.append("ఇంకా అప్‌డేట్ ఇవ్వలేదు." if telugu else "No update has been posted yet.")
            continue
        found_any = True
        for n in matching:
            msg = (n.get("message_te") if telugu and n.get("message_te") else n.get("message_en")) or ""
            lines.append(msg.strip())
            ts = _parse(n.get("updated_at"))
            if ts and (newest is None or ts > newest):
                newest = ts
    lines.append("")
    if newest:
        stamp = newest.astimezone(IST).strftime("%d %b, %I:%M %p")
        lines.append(("🕐 చివరి అప్‌డేట్: " if telugu else "🕐 Last updated: ") + stamp)
    lines.append("ℹ️ " + ("అధికారిక సమాచారం కోసం https://tirumala.org చూడండి." if telugu
                          else "Please confirm on the official site https://tirumala.org."))
    return {"reply": "\n".join(lines).strip(), "topic": topic, "found": found_any}
