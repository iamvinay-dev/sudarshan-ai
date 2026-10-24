# -*- coding: utf-8 -*-
"""
admin_extra.py
--------------
More pages for the admin website (admin.py stays unchanged; this file plugs into it):

    Live notices   - staff type SSD token timings, ticket availability, one-day rules.
                     The bot shows them to pilgrims (see notices.py).
    Complaints     - every complaint / "question not solved" report, with a 24-hour deadline,
                     status, notes, assignment, and a way to contact the pilgrim.
    Bribe reports  - same, but only for the roles vigilance / senior / super.
    Feedback       - solved %, ratings, unsolved questions.
    New look       - sidebar menu, extra dashboard cards.

HOW THE PILGRIM IS CONTACTED (privacy):
    * "Send WhatsApp message" - the SERVER sends the message. The officer never sees the number.
      WhatsApp only allows this within 24 hours after the pilgrim's last message.
    * "Show number to call" - only roles senior / vigilance / super, never for anonymous
      reports. Every use is written to the audit log and the complaint timeline.
    * Pilgrims who chose "anonymous" can never be contacted.

Roles (column admin_users.role): officer (default), senior, vigilance, super.
"""

import re
import time
import logging
from collections import Counter
from datetime import timedelta

from flask import request, redirect, url_for, flash, g, abort, jsonify, make_response

import admin as A
import db
import notices

log = logging.getLogger("sudarshan-ai.admin_extra")
bp = A.bp

SEND = None                                   # set by app.py: SEND(number, text) -> (ok, error)
BRIBE_ROLES = {"vigilance", "senior", "super"}
REVEAL_ROLES = {"vigilance", "senior", "super"}
PAGE = 50

STATUS_LABELS = {"new": "New", "in_progress": "In progress", "resolved": "Resolved", "escalated": "Escalated"}
CAT_LABELS = {"darshan": "Darshan / queue", "accommodation": "Accommodation", "transport": "Transport",
              "staff": "Staff behaviour", "bribe": "Bribe / corruption", "other": "Other",
              "unsolved": "Question not solved"}
WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

# ---- teach admin.py about the new sources / categories / languages ----
for _s in ("notice", "complaint", "feedback"):
    if _s not in A.SOURCES:
        A.SOURCES.append(_s)
A.SOURCE_LABELS.update(notice="Live notice", complaint="Complaint", feedback="Feedback")
for _c in ("greeting", "clarify", "notice", "complaint", "feedback", "language", "other", "bribe", "staff", "unsolved"):
    if _c not in A.CATEGORIES:
        A.CATEGORIES.append(_c)
A.CATEGORY_LABELS.update(greeting="Greeting", clarify="Needs more detail", notice="Live notice",
                         complaint="Complaint", feedback="Feedback", language="Language change",
                         other="Other / general", unknown="Other / general", staff="Staff behaviour",
                         bribe="Bribe report", unsolved="Not solved")
_LANGS = {"te-latin": "Telugu (English letters)", "hi": "Hindi", "kn": "Kannada", "ta": "Tamil",
          "ml": "Malayalam", "bn": "Bengali", "gu": "Gujarati", "or": "Odia", "pa": "Punjabi", "ur": "Urdu"}
for _k, _v in _LANGS.items():
    if _k not in A.LANGS:
        A.LANGS.append(_k)
A.LANG_LABELS.update(_LANGS)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
_role_cache = {}


def role():
    uid = g.user["id"]
    cached = _role_cache.get(uid)
    if cached and cached[1] > time.time():
        return cached[0]
    rows = A._get("admin_users", {"select": "role", "id": f"eq.{uid}", "limit": "1"})
    r = ((rows[0].get("role") if rows else None) or "officer").lower()
    _role_cache[uid] = (r, time.time() + 60)
    return r


def can_bribe():
    try:
        return role() in BRIBE_ROLES
    except Exception:  # noqa: BLE001
        return False


A._env.globals["can_bribe"] = lambda: bool(g.get("user")) and can_bribe()


def _csrf():
    if not A.csrf_ok():
        flash("Please try again.", "error")
        return False
    return True


def _now_iso():
    return A.iso(A.now_utc())


def _span(secs):
    secs = abs(int(secs))
    h, m = secs // 3600, (secs % 3600) // 60
    return f"{h}h {m}m" if h else f"{m}m"


def _left(row):
    if row.get("status") == "resolved":
        return "Resolved", "ok"
    due = A.parse_ts(row.get("due_at"))
    if not due:
        return "-", ""
    secs = (due - A.now_utc()).total_seconds()
    if secs < 0:
        return "Overdue " + _span(secs), "bad"
    return _span(secs) + " left", ("warn" if secs < 4 * 3600 else "")


def _event(cid, event, note=None):
    db._request("POST", "complaint_events", prefer="return=minimal",
                body={"complaint_id": cid, "admin_id": g.user["id"], "event": event, "note": (note or "")[:1000]})


_esc = {"t": 0.0}


def escalate_overdue(force=False):
    """Complaints still open 24 hours after they were created become 'escalated'."""
    if not force and time.time() - _esc["t"] < 60:
        return 0
    _esc["t"] = time.time()
    now = _now_iso()
    rows = db._json(db._request("PATCH", "complaints", prefer="return=representation",
                                params={"status": "in.(new,in_progress)", "due_at": f"lt.{now}"},
                                body={"status": "escalated", "escalated_at": now})) or []
    if rows:
        db._request("POST", "complaint_events", prefer="return=minimal",
                    body=[{"complaint_id": r["id"], "event": "escalated",
                           "note": "Not resolved within 24 hours"} for r in rows])
    return len(rows)


# ---------------------------------------------------------------------------
# Live notices
# ---------------------------------------------------------------------------
@bp.route("/notices")
@A.login_required
def notices_page():
    today = notices.ist_today()
    rows = A._get("notices", {"select": "*", "order": "id.desc", "limit": "200"})
    if rows is None:
        return A.render("message.html", title="Please wait", text="Could not load notices. Try again."), 503
    for r in rows:
        vf, vt = str(r.get("valid_from"))[:10], str(r.get("valid_to"))[:10]
        r["topic_label"] = notices.TOPICS.get(r.get("topic"), {}).get("en", r.get("topic"))
        r["weekday_label"] = WEEKDAYS[r["weekday"]] if isinstance(r.get("weekday"), int) else "Every day"
        r["live"] = bool(r.get("active")) and notices._applies(r, today)
        r["expired"] = vt < today.isoformat()
        r["updated"] = A.fmt_ist(r.get("updated_at"))
    edit = None
    edit_id = request.args.get("edit", type=int)
    if edit_id:
        edit = next((r for r in rows if r["id"] == edit_id), None)
    return A.render("notices.html", active="notices", rows=rows, edit=edit, today=today.isoformat(),
                    topics=notices.TOPICS, weekdays=list(enumerate(WEEKDAYS)))


@bp.route("/notices/save", methods=["POST"])
@A.login_required
def notices_save():
    if not _csrf():
        return redirect(url_for("admin.notices_page"))
    f = request.form
    nid = f.get("id", type=int)
    topic = f.get("topic", "")
    msg_en = f.get("message_en", "").strip()[:1000]
    msg_te = f.get("message_te", "").strip()[:1000] or None
    d1, d2 = A.parse_date(f.get("valid_from")), A.parse_date(f.get("valid_to"))
    wd = f.get("weekday", "")
    weekday = int(wd) if wd.isdigit() and 0 <= int(wd) <= 6 else None
    problem = None
    if topic not in notices.TOPICS:
        problem = "Please choose a topic."
    elif len(msg_en) < 3:
        problem = "Please type the message pilgrims should see."
    elif not d1 or not d2:
        problem = "Please choose both dates."
    elif d2 < d1:
        problem = "The 'to' date cannot be before the 'from' date."
    if problem:
        flash(problem, "error")
        return redirect(url_for("admin.notices_page", edit=nid) if nid else url_for("admin.notices_page"))
    body = {"topic": topic, "message_en": msg_en, "message_te": msg_te, "valid_from": d1.isoformat(),
            "valid_to": d2.isoformat(), "weekday": weekday, "active": f.get("active") == "1",
            "updated_at": _now_iso(), "updated_by": g.user["id"]}
    if nid:
        resp = db._request("PATCH", "notices", params={"id": f"eq.{nid}"}, body=body, prefer="return=minimal")
    else:
        resp = db._request("POST", "notices", body=body, prefer="return=minimal")
    if resp is None:
        flash("Could not save. Please try again.", "error")
    else:
        notices.invalidate()
        A.audit(g.user["id"], f"notice_{'edited' if nid else 'added'}:{topic}")
        flash("Saved. Pilgrims will see this within about 30 seconds.", "ok")
    return redirect(url_for("admin.notices_page"))


@bp.route("/notices/<int:nid>/toggle", methods=["POST"])
@A.login_required
def notices_toggle(nid):
    if _csrf():
        rows = A._get("notices", {"select": "active", "id": f"eq.{nid}", "limit": "1"})
        if rows:
            db._request("PATCH", "notices", params={"id": f"eq.{nid}"}, prefer="return=minimal",
                        body={"active": not rows[0].get("active"), "updated_at": _now_iso(),
                              "updated_by": g.user["id"]})
            notices.invalidate()
            A.audit(g.user["id"], f"notice_toggled:{nid}")
    return redirect(url_for("admin.notices_page"))


@bp.route("/notices/<int:nid>/delete", methods=["POST"])
@A.login_required
def notices_delete(nid):
    if _csrf():
        db._request("DELETE", "notices", params={"id": f"eq.{nid}"}, prefer="return=minimal")
        notices.invalidate()
        A.audit(g.user["id"], f"notice_deleted:{nid}")
        flash("Notice deleted.", "ok")
    return redirect(url_for("admin.notices_page"))


# ---------------------------------------------------------------------------
# Complaints and bribe reports
# ---------------------------------------------------------------------------
LIST_COLS = ("id,ref,pilgrim_id,created_at,category,is_bribe,anonymous,language,status,"
             "assigned_to,due_at,source")


def _complaint_list(bribe_only):
    escalate_overdue()
    a = request.args
    f = {"status": a.get("status", "").strip(), "category": a.get("category", "").strip(),
         "language": a.get("language", "").strip(), "overdue": a.get("overdue", "") == "1"}
    params = {}
    if bribe_only:
        params["is_bribe"] = "eq.true"
    elif not can_bribe():
        params["is_bribe"] = "eq.false"
    if f["status"] == "open":
        params["status"] = "in.(new,in_progress,escalated)"
    elif f["status"] in STATUS_LABELS:
        params["status"] = "eq." + f["status"]
    else:
        f["status"] = ""
    if f["category"] in CAT_LABELS:
        params["category"] = "eq." + f["category"]
    else:
        f["category"] = ""
    if re.fullmatch(r"[a-z\-]{2,8}", f["language"]):
        params["language"] = "eq." + f["language"]
    else:
        f["language"] = ""
    if f["overdue"]:
        params["due_at"] = "lt." + _now_iso()
        params.setdefault("status", "in.(new,in_progress,escalated)")
    page = min(max(request.args.get("page", 1, type=int) or 1, 1), 2000)
    total = A._count("complaints", params)
    rows = A._get("complaints", {**params, "select": LIST_COLS, "order": "id.desc",
                                 "limit": str(PAGE), "offset": str((page - 1) * PAGE)})
    if rows is None:
        return A.render("message.html", title="Please wait", text="Could not load complaints."), 503
    codes = A.codes_for([r.get("pilgrim_id") for r in rows])
    admins = {}
    ids = {r["assigned_to"] for r in rows if r.get("assigned_to")}
    if ids:
        for u in A._get("admin_users", {"select": "id,username", "id": "in.(" + ",".join(map(str, ids)) + ")"}) or []:
            admins[u["id"]] = u["username"]
    for r in rows:
        r["code"] = codes.get(r.get("pilgrim_id"), "#?")
        r["when"] = A.fmt_ist(r.get("created_at"))
        r["left"], r["left_cls"] = _left(r)
        r["cat_label"] = CAT_LABELS.get(r.get("category"), r.get("category"))
        r["assignee"] = admins.get(r.get("assigned_to"), "")
    args = {k: v for k, v in {"status": f["status"], "category": f["category"], "language": f["language"],
                              "overdue": "1" if f["overdue"] else ""}.items() if v}
    return A.render("complaints.html", active="bribe" if bribe_only else "complaints", rows=rows, f=f,
                    total=total, page=page, pages=max(1, -(-(total or 0) // PAGE)), args=args,
                    bribe_only=bribe_only, cats=CAT_LABELS, statuses=STATUS_LABELS,
                    langs=A.LANGS, langlabels=A.LANG_LABELS)


@bp.route("/complaints")
@A.login_required
def complaints_page():
    return _complaint_list(False)


@bp.route("/bribe-reports")
@A.login_required
def bribe_page():
    if not can_bribe():
        abort(403)
    return _complaint_list(True)


def _load(ref):
    if not re.fullmatch(r"C-\d{3,9}", ref or ""):
        abort(404)
    rows = A._get("complaints", {"select": "*", "ref": f"eq.{ref}", "limit": "1"})
    if rows is None:
        abort(503)
    if not rows or (rows[0].get("is_bribe") and not can_bribe()):
        abort(404)
    return rows[0]


@bp.route("/complaint/<ref>")
@A.login_required
def complaint_page(ref):
    escalate_overdue()
    c = _load(ref)
    events = A._get("complaint_events", {"select": "*", "complaint_id": f"eq.{c['id']}", "order": "id.asc"}) or []
    ids = {e["admin_id"] for e in events if e.get("admin_id")} | ({c["assigned_to"]} if c.get("assigned_to") else set())
    names = {}
    if ids:
        for u in A._get("admin_users", {"select": "id,username", "id": "in.(" + ",".join(map(str, ids)) + ")"}) or []:
            names[u["id"]] = u["username"]
    for e in events:
        e["when"] = A.fmt_ist(e.get("created_at"), seconds=False)
        e["who"] = names.get(e.get("admin_id"), "Bot" if not e.get("admin_id") else "?")
    can_msg = False
    if not c.get("anonymous") and db.contact_enabled() and c.get("pilgrim_id"):
        has = A._get("pilgrims", {"select": "id", "id": f"eq.{c['pilgrim_id']}", "phone_enc": "not.is.null", "limit": "1"})
        can_msg = bool(has)
    left, left_cls = _left(c)
    return A.render("complaint.html", active="bribe" if c.get("is_bribe") else "complaints", c=c, events=events,
                    code=A.codes_for([c.get("pilgrim_id")]).get(c.get("pilgrim_id"), "#?"),
                    created=A.fmt_ist(c.get("created_at")), due=A.fmt_ist(c.get("due_at")),
                    left=left, left_cls=left_cls, cat_label=CAT_LABELS.get(c.get("category"), c.get("category")),
                    status_label=STATUS_LABELS.get(c.get("status"), c.get("status")),
                    assignee=names.get(c.get("assigned_to"), ""), can_msg=can_msg,
                    can_reveal=can_msg and role() in REVEAL_ROLES)


@bp.route("/complaint/<ref>/action", methods=["POST"])
@A.login_required
def complaint_action(ref):
    c = _load(ref)
    back = redirect(url_for("admin.complaint_page", ref=ref))
    if not _csrf():
        return back
    do = request.form.get("do", "")
    note = request.form.get("note", "").strip()[:1000]
    now = _now_iso()
    patch, event = None, None
    if do == "assign_me":
        patch = {"assigned_to": g.user["id"]}
        if c["status"] == "new":
            patch["status"] = "in_progress"
        event = "assigned"
    elif do == "in_progress":
        patch, event = {"status": "in_progress"}, "in_progress"
    elif do == "escalate":
        patch, event = {"status": "escalated", "escalated_at": now}, "escalated"
    elif do == "reopen":
        patch, event = {"status": "in_progress", "resolved_at": None}, "reopened"
    elif do == "resolve":
        if len(note) < 3:
            flash("Please write a short resolution note.", "error")
            return back
        patch, event = {"status": "resolved", "resolved_at": now, "resolution_note": note}, "resolved"
    elif do == "note":
        if len(note) < 2:
            flash("Please type a note.", "error")
            return back
        event = "note"
    else:
        abort(400)
    if patch and db._request("PATCH", "complaints", params={"id": f"eq.{c['id']}"}, body=patch,
                             prefer="return=minimal") is None:
        flash("Could not save. Please try again.", "error")
        return back
    _event(c["id"], event, note)
    A.audit(g.user["id"], f"complaint_{event}:{ref}")
    flash("Saved.", "ok")
    return back


def _pilgrim_number(c):
    rows = A._get("pilgrims", {"select": "phone_enc", "id": f"eq.{c['pilgrim_id']}", "limit": "1"})
    token = rows[0].get("phone_enc") if rows else None
    return db.decrypt_phone(token) if token else None


@bp.route("/complaint/<ref>/message", methods=["POST"])
@A.login_required
def complaint_message(ref):
    c = _load(ref)
    back = redirect(url_for("admin.complaint_page", ref=ref))
    if not _csrf():
        return back
    text = request.form.get("text", "").strip()[:800]
    if len(text) < 2:
        flash("Please type a message.", "error")
        return back
    if c.get("anonymous") or not db.contact_enabled() or SEND is None:
        flash("This pilgrim cannot be contacted.", "error")
        return back
    try:
        number = _pilgrim_number(c)
    except Exception as exc:  # noqa: BLE001
        log.error("Could not read the number: %s", type(exc).__name__)
        number = None
    if not number:
        flash("No contact number is stored for this pilgrim.", "error")
        return back
    ok, err = SEND(number, f"🙏 *TTD Support* (Ref {ref})\n\n{text}\n\n— TTD Admin Team")
    if not ok:
        if "131047" in (err or "") or "24" in (err or "") and "hour" in (err or ""):
            flash("WhatsApp blocked the message: the pilgrim has not written to us in the last 24 hours. "
                  "Ask them to send a message to the bot first, or use 'Show number to call'.", "error")
        else:
            flash("The message could not be sent. Please try again later.", "error")
        return back
    if c["status"] == "new":
        db._request("PATCH", "complaints", params={"id": f"eq.{c['id']}"}, body={"status": "in_progress"},
                    prefer="return=minimal")
    _event(c["id"], "message_sent", text)
    A.audit(g.user["id"], f"complaint_message_sent:{ref}")
    flash("Message sent to the pilgrim on WhatsApp.", "ok")
    return back


@bp.route("/complaint/<ref>/reveal", methods=["POST"])
@A.login_required
def complaint_reveal(ref):
    c = _load(ref)
    if not _csrf():
        return redirect(url_for("admin.complaint_page", ref=ref))
    if role() not in REVEAL_ROLES or c.get("anonymous") or not db.contact_enabled():
        abort(403)
    try:
        number = _pilgrim_number(c)
    except Exception:  # noqa: BLE001
        number = None
    if not number:
        flash("No contact number is stored for this pilgrim.", "error")
        return redirect(url_for("admin.complaint_page", ref=ref))
    _event(c["id"], "number_revealed", "Number shown to call")
    A.audit(g.user["id"], f"number_revealed:{ref}")
    return A.render("message.html", title=f"Contact for {ref}",
                    text=f"Pilgrim number: +{number}   (open https://wa.me/{number} to chat on WhatsApp). "
                         "This view has been recorded in the audit log.")


# ---------------------------------------------------------------------------
# Feedback
# ---------------------------------------------------------------------------
@bp.route("/feedback")
@A.login_required
def feedback_page():
    rows = A._get("feedback", {"select": "id,pilgrim_id,created_at,solved,rating,last_question,problem_text,topic,category",
                               "order": "id.desc", "limit": "500"})
    if rows is None:
        return A.render("message.html", title="Please wait", text="Could not load feedback."), 503
    solved = sum(1 for r in rows if r.get("solved"))
    ratings = [int(r["rating"]) for r in rows if str(r.get("rating") or "").isdigit()]
    dist = Counter(ratings)
    codes = A.codes_for([r.get("pilgrim_id") for r in rows])
    bad = [{"when": A.fmt_ist(r.get("created_at")), "code": codes.get(r.get("pilgrim_id"), "#?"),
            "q": r.get("last_question") or "", "p": r.get("problem_text") or ""}
           for r in rows if r.get("solved") is False][:100]
    return A.render("feedback.html", active="feedback", total=len(rows), solved=solved,
                    pct=round(100.0 * solved / len(rows), 1) if rows else None,
                    avg=round(sum(ratings) / len(ratings), 2) if ratings else None,
                    dist=[(i, dist.get(i, 0)) for i in range(5, 0, -1)], bad=bad)


# ---------------------------------------------------------------------------
# Dashboard extra numbers
# ---------------------------------------------------------------------------
_ov = {"t": 0.0, "d": None}


@bp.route("/api/overview")
@A.login_required
def api_overview():
    if _ov["d"] and time.time() - _ov["t"] < 10 and _ov.get("role") == role():
        return jsonify(_ov["d"])
    escalate_overdue()
    bribe_ok = can_bribe()
    base = {} if bribe_ok else {"is_bribe": "eq.false"}
    open_p = {**base, "status": "in.(new,in_progress,escalated)"}
    fb = A._get("feedback", {"select": "solved,rating", "order": "id.desc", "limit": "500"}) or []
    ratings = [int(r["rating"]) for r in fb if str(r.get("rating") or "").isdigit()]
    live = sum(1 for n in (notices.fetch_active() or [])
               if notices._applies(n, notices.ist_today()))
    data = {"open": A._count("complaints", open_p),
            "overdue": A._count("complaints", {**open_p, "due_at": "lt." + _now_iso()}),
            "bribe": A._count("complaints", {"is_bribe": "eq.true", "status": "in.(new,in_progress,escalated)"}) if bribe_ok else None,
            "solved_pct": round(100.0 * sum(1 for r in fb if r.get("solved")) / len(fb), 1) if fb else None,
            "rating": round(sum(ratings) / len(ratings), 2) if ratings else None,
            "notices": live}
    _ov.update(t=time.time(), d=data, role=role())
    return jsonify(data)


# ---------------------------------------------------------------------------
# Look and feel: sidebar layout, badges, extra dashboard cards
# ---------------------------------------------------------------------------
EXTRA_CSS = r"""
body.app{background:#FBF4E8}
.shell{display:flex;min-height:100vh}
.side{width:230px;flex:0 0 230px;background:var(--maroon);color:#fff;padding:16px 12px;display:flex;flex-direction:column;gap:14px;position:sticky;top:0;height:100vh;border-right:4px solid var(--saffron)}
.side .brand{font-size:1.05rem;line-height:1.2}.side .brand small{display:block;opacity:.75;font-size:.78rem}
.side nav{display:flex;flex-direction:column;gap:4px;flex:1}
.side a{color:#fff;text-decoration:none;padding:9px 12px;border-radius:8px;font-size:.93rem}
.side a:hover{background:var(--maroon2)}.side a.on{background:var(--saffron);color:#2B1B17;font-weight:600}
.side form{margin:0}.side button{width:100%;background:transparent;color:#fff;border:1px solid rgba(255,255,255,.4);border-radius:8px;padding:8px;cursor:pointer}
.main{flex:1;min-width:0}
.badge{display:inline-block;padding:2px 9px;border-radius:99px;font-size:.75rem;font-weight:600}
.b-new{background:#dbe9fb;color:#0d3c78}.b-in_progress{background:#fde7c4;color:#7a4300}
.b-resolved{background:#d9f0dc;color:#1b5e20}.b-escalated{background:#fadbd8;color:#a1241b}
.t-bad{color:var(--bad);font-weight:700}.t-warn{color:#b26a00;font-weight:600}.t-ok{color:var(--ok)}
.s-notice{background:#d6f1f5;color:#0b5560}.s-complaint{background:#fadbd8;color:#a1241b}.s-feedback{background:#e8e0f7;color:#4a2f8a}
.card.warn .v{color:#a1241b}
textarea{width:100%;padding:9px 10px;border:1px solid #cdb995;border-radius:7px;font-size:1rem;font-family:inherit;min-height:90px}
.row2{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px}
.timeline{list-style:none;margin:0;padding:0}.timeline li{border-left:3px solid var(--saffron);padding:4px 0 10px 12px;margin-left:6px}
.timeline small{color:#7a6659}
.actions{display:flex;flex-wrap:wrap;gap:8px;align-items:center}.actions form{margin:0}
button.sm,.actions button{padding:7px 12px;border-radius:7px;border:1px solid var(--maroon);background:#fff;color:var(--maroon);cursor:pointer;font-size:.88rem}
button.sm:hover,.actions button:hover{background:var(--maroon);color:#fff}button.danger{border-color:var(--bad);color:var(--bad)}
.details{white-space:pre-wrap;background:#fffaf0;border:1px solid var(--line);border-radius:8px;padding:10px}
.bars div{display:flex;align-items:center;gap:8px;margin:4px 0}.bars i{display:block;height:12px;background:var(--saffron);border-radius:6px}
@media(max-width:820px){.shell{display:block}.side{position:static;width:auto;height:auto;flex-direction:column}.side nav{flex-direction:row;flex-wrap:wrap}}
"""

NEW_BASE = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<title>{% block title %}Admin{% endblock %} – Sudarshan AI – TTD Admin</title>
<link rel="stylesheet" href="{{ url_for('admin.asset_css') }}">
</head><body class="{{ 'app' if user else 'auth' }}">
{% if user %}<div class="shell"><aside class="side">
<div class="brand">🛕 <b>Sudarshan AI</b><small>TTD Admin Panel</small></div>
<nav>
<a href="{{ url_for('admin.dashboard') }}" class="{{ 'on' if active == 'dashboard' }}">📊 Dashboard</a>
<a href="{{ url_for('admin.complaints_page') }}" class="{{ 'on' if active == 'complaints' }}">📝 Complaints</a>
{% if can_bribe() %}<a href="{{ url_for('admin.bribe_page') }}" class="{{ 'on' if active == 'bribe' }}">🚫 Bribe reports</a>{% endif %}
<a href="{{ url_for('admin.notices_page') }}" class="{{ 'on' if active == 'notices' }}">🔔 Live notices</a>
<a href="{{ url_for('admin.queries') }}" class="{{ 'on' if active == 'queries' }}">💬 Questions</a>
<a href="{{ url_for('admin.feedback_page') }}" class="{{ 'on' if active == 'feedback' }}">⭐ Feedback</a>
<a href="{{ url_for('admin.change_password') }}">🔑 Change password</a>
</nav>
<form method="post" action="{{ url_for('admin.logout') }}"><input type="hidden" name="csrf_token" value="{{ csrf() }}"><button type="submit">Log out</button></form>
</aside><section class="main">
{% else %}<header class="top"><h2>🛕 Sudarshan AI – TTD Admin</h2></header>{% endif %}
<main class="wrap">
{% for cat, text in messages %}<div class="msg {{ cat }}">{{ text }}</div>{% endfor %}
{% block content %}{% endblock %}
</main>
{% if user %}</section></div>{% endif %}
{% if charts %}<script src="{{ chartjs }}" defer></script>{% endif %}
<script src="{{ url_for('admin.asset_js') }}" defer></script>
<script src="{{ url_for('admin.asset_extra_js') }}" defer></script>
</body></html>"""

EXTRA_CARDS = """<section class="cards">
<div class="card warn"><div class="k">Open complaints</div><div class="v" id="xOpen">–</div><div class="s"><a href="/admin/complaints?status=open">View</a></div></div>
<div class="card"><div class="k">Overdue (24 h)</div><div class="v" id="xOverdue">–</div><div class="s"><a href="/admin/complaints?overdue=1">View</a></div></div>
{% if can_bribe() %}<div class="card warn"><div class="k">Bribe reports open</div><div class="v" id="xBribe">–</div><div class="s"><a href="/admin/bribe-reports">View</a></div></div>{% endif %}
<div class="card"><div class="k">Question solved</div><div class="v" id="xSolved">–</div><div class="s" id="xRating"></div></div>
<div class="card"><div class="k">Live notices today</div><div class="v" id="xNotices">–</div><div class="s"><a href="/admin/notices">Manage</a></div></div>
</section>
"""

EXTRA_JS = r"""
(function () {
  "use strict";
  function $(id) { return document.getElementById(id); }
  function set(id, v) { var e = $(id); if (e) { e.textContent = (v === null || v === undefined) ? "–" : String(v); } }
  function load() {
    if (!$("xOpen")) { return; }
    fetch("/admin/api/overview", { credentials: "same-origin", cache: "no-store" })
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(function (d) {
        if (!d) { return; }
        set("xOpen", d.open); set("xOverdue", d.overdue); set("xBribe", d.bribe);
        set("xSolved", d.solved_pct === null ? null : d.solved_pct + "%");
        set("xRating", d.rating === null ? "" : "Average rating " + d.rating + " / 5");
        set("xNotices", d.notices);
      }).catch(function () {});
  }
  load(); setInterval(function () { if (!document.hidden) { load(); } }, 15000);
})();
"""

T = {}

T["notices.html"] = r"""{% extends "base.html" %}
{% block title %}Live notices{% endblock %}
{% block content %}
<h1>🔔 Live notices</h1>
<p class="muted">Type today's SSD token timing, ticket availability or a one-day rule here. When a pilgrim asks
about it, the bot shows exactly what you write (for the dates you choose). If nothing is posted, the bot says
"no update posted yet" and points to tirumala.org.</p>
<form method="post" action="{{ url_for('admin.notices_save') }}" class="panel">
<h3>{{ 'Edit notice' if edit else 'Add a new notice' }}</h3>
<input type="hidden" name="csrf_token" value="{{ csrf() }}">
{% if edit %}<input type="hidden" name="id" value="{{ edit.id }}">{% endif %}
<div class="row2">
<div><label>Topic</label><select name="topic">{% for k, t in topics.items() %}<option value="{{ k }}" {{ 'selected' if edit and edit.topic == k }}>{{ t.en }}</option>{% endfor %}</select></div>
<div><label>Valid from</label><input type="date" name="valid_from" value="{{ edit.valid_from if edit else today }}" required></div>
<div><label>Valid to</label><input type="date" name="valid_to" value="{{ edit.valid_to if edit else today }}" required></div>
<div><label>Repeat on</label><select name="weekday"><option value="">Every day in this range</option>{% for i, d in weekdays %}<option value="{{ i }}" {{ 'selected' if edit and edit.weekday == i }}>Only on {{ d }}</option>{% endfor %}</select></div>
</div>
<label>Message for pilgrims (English) *</label>
<textarea name="message_en" maxlength="1000" required>{{ edit.message_en if edit else '' }}</textarea>
<label>Message in Telugu (optional; English is shown if empty)</label>
<textarea name="message_te" maxlength="1000">{{ edit.message_te if edit and edit.message_te else '' }}</textarea>
<label><input type="checkbox" name="active" value="1" style="width:auto" {{ 'checked' if (not edit) or edit.active }}> Active (untick to hide it without deleting)</label>
<button class="go" type="submit">Save notice</button>
{% if edit %} <a href="{{ url_for('admin.notices_page') }}">Cancel</a>{% endif %}
</form>
<p class="muted" style="margin-top:10px">Examples: <b>SSD Tokens</b>, from today to today: "Token counters open at 5:00 AM at Bhudevi complex."
&nbsp;|&nbsp; <b>VIP Break Darshan</b>, repeat on Wednesday: "VIP break darshan tickets are not issued on Wednesdays because of Abhishekam."
Always write only what TTD has officially announced.</p>
<div class="panel scroll" style="margin-top:12px"><h3>All notices</h3><table>
<thead><tr><th>Status</th><th>Topic</th><th>Message</th><th>Dates</th><th>Repeat</th><th>Updated</th><th></th></tr></thead><tbody>
{% for r in rows %}<tr>
<td>{% if r.live %}<span class="badge b-resolved">Live now</span>{% elif r.expired %}<span class="badge">Expired</span>{% elif not r.active %}<span class="badge">Paused</span>{% else %}<span class="badge b-new">Scheduled</span>{% endif %}</td>
<td>{{ r.topic_label }}</td><td class="q">{{ r.message_en }}</td>
<td>{{ r.valid_from }} → {{ r.valid_to }}</td><td>{{ r.weekday_label }}</td><td>{{ r.updated }}</td>
<td class="actions"><a href="{{ url_for('admin.notices_page', edit=r.id) }}">Edit</a>
<form method="post" action="{{ url_for('admin.notices_toggle', nid=r.id) }}"><input type="hidden" name="csrf_token" value="{{ csrf() }}"><button type="submit">{{ 'Pause' if r.active else 'Activate' }}</button></form>
<form method="post" action="{{ url_for('admin.notices_delete', nid=r.id) }}"><input type="hidden" name="csrf_token" value="{{ csrf() }}"><button type="submit" class="danger">Delete</button></form></td>
</tr>{% else %}<tr><td colspan="7" class="muted">No notices yet. Add the first one above.</td></tr>{% endfor %}
</tbody></table></div>
{% endblock %}"""

T["complaints.html"] = r"""{% extends "base.html" %}
{% block title %}{{ 'Bribe reports' if bribe_only else 'Complaints' }}{% endblock %}
{% block content %}
<div class="bar"><h1>{{ '🚫 Bribe reports' if bribe_only else '📝 Complaints' }}</h1></div>
<form method="get" class="panel filters">
<div><label>Status</label><select name="status"><option value="">All</option><option value="open" {{ 'selected' if f.status == 'open' }}>Open (not resolved)</option>{% for k, v in statuses.items() %}<option value="{{ k }}" {{ 'selected' if f.status == k }}>{{ v }}</option>{% endfor %}</select></div>
<div><label>Category</label><select name="category"><option value="">All</option>{% for k, v in cats.items() %}<option value="{{ k }}" {{ 'selected' if f.category == k }}>{{ v }}</option>{% endfor %}</select></div>
<div><label>Language</label><select name="language"><option value="">All</option>{% for l in langs %}<option value="{{ l }}" {{ 'selected' if f.language == l }}>{{ langlabels.get(l, l) }}</option>{% endfor %}</select></div>
<div><label><input type="checkbox" name="overdue" value="1" style="width:auto" {{ 'checked' if f.overdue }}> Overdue only</label></div>
<div><button class="go" type="submit">Filter</button></div>
</form>
<p class="muted">{{ total if total is not none else '?' }} found. Times are India time (IST). Each complaint must be handled within 24 hours, or it is escalated.</p>
<div class="panel scroll"><table>
<thead><tr><th>Ref</th><th>Time</th><th>Category</th><th>Status</th><th>Time left</th><th>Language</th><th>Pilgrim</th><th>Assigned</th></tr></thead><tbody>
{% for r in rows %}<tr>
<td><a href="{{ url_for('admin.complaint_page', ref=r.ref) }}"><b>{{ r.ref }}</b></a>{% if r.anonymous %} 🔒{% endif %}</td>
<td>{{ r.when }}</td><td>{{ r.cat_label }}</td>
<td><span class="badge b-{{ r.status }}">{{ statuses.get(r.status, r.status) }}</span></td>
<td class="t-{{ r.left_cls }}">{{ r.left }}</td><td>{{ langlabels.get(r.language, r.language or '') }}</td>
<td>{% if r.anonymous and r.is_bribe %}Anonymous{% else %}{{ r.code }}{% endif %}</td><td>{{ r.assignee }}</td></tr>
{% else %}<tr><td colspan="8" class="muted">Nothing here yet. 🙏</td></tr>{% endfor %}
</tbody></table></div>
<div class="pager">
{% if page > 1 %}<a href="{{ url_for('admin.bribe_page' if bribe_only else 'admin.complaints_page', page=page-1, **args) }}">← Newer</a>{% endif %}
<span>Page {{ page }} of {{ pages }}</span>
{% if page < pages %}<a href="{{ url_for('admin.bribe_page' if bribe_only else 'admin.complaints_page', page=page+1, **args) }}">Older →</a>{% endif %}
</div>{% endblock %}"""

T["complaint.html"] = r"""{% extends "base.html" %}
{% block title %}{{ c.ref }}{% endblock %}
{% block content %}
<p><a href="{{ url_for('admin.bribe_page' if c.is_bribe else 'admin.complaints_page') }}">← Back to list</a></p>
<h1>{{ c.ref }} {% if c.is_bribe %}🚫{% endif %} <span class="badge b-{{ c.status }}">{{ status_label }}</span></h1>
<section class="cards">
<div class="card"><div class="k">Category</div><div class="s">{{ cat_label }}</div></div>
<div class="card"><div class="k">Received</div><div class="s">{{ created }}</div></div>
<div class="card"><div class="k">Deadline</div><div class="s">{{ due }}</div><div class="t-{{ left_cls }}">{{ left }}</div></div>
<div class="card"><div class="k">Pilgrim</div><div class="s">{% if c.anonymous %}Anonymous 🔒{% else %}{{ code }}{% endif %}</div></div>
<div class="card"><div class="k">Assigned to</div><div class="s">{{ assignee or 'Nobody yet' }}</div></div>
</section>
<div class="panel"><h3>What the pilgrim wrote</h3><div class="details">{{ c.details }}</div>
{% if c.last_question %}<p class="muted">Last question before this: {{ c.last_question }}</p>{% endif %}
{% if c.resolution_note %}<h3 style="margin-top:12px">Resolution note</h3><div class="details">{{ c.resolution_note }}</div>{% endif %}</div>

<div class="panel" style="margin-top:12px"><h3>Actions</h3>
<div class="actions">
<form method="post" action="{{ url_for('admin.complaint_action', ref=c.ref) }}"><input type="hidden" name="csrf_token" value="{{ csrf() }}"><input type="hidden" name="do" value="assign_me"><button type="submit">Assign to me</button></form>
<form method="post" action="{{ url_for('admin.complaint_action', ref=c.ref) }}"><input type="hidden" name="csrf_token" value="{{ csrf() }}"><input type="hidden" name="do" value="in_progress"><button type="submit">Mark in progress</button></form>
<form method="post" action="{{ url_for('admin.complaint_action', ref=c.ref) }}"><input type="hidden" name="csrf_token" value="{{ csrf() }}"><input type="hidden" name="do" value="escalate"><button type="submit" class="danger">Escalate</button></form>
{% if c.status == 'resolved' %}<form method="post" action="{{ url_for('admin.complaint_action', ref=c.ref) }}"><input type="hidden" name="csrf_token" value="{{ csrf() }}"><input type="hidden" name="do" value="reopen"><button type="submit">Reopen</button></form>{% endif %}
</div>
<form method="post" action="{{ url_for('admin.complaint_action', ref=c.ref) }}">
<input type="hidden" name="csrf_token" value="{{ csrf() }}">
<label>Note or resolution</label><textarea name="note" maxlength="1000" placeholder="Write what was done"></textarea>
<div class="actions" style="margin-top:8px"><button type="submit" name="do" value="note">Add note</button><button type="submit" name="do" value="resolve">✅ Resolve with this note</button></div>
</form></div>

<div class="panel" style="margin-top:12px"><h3>Contact the pilgrim</h3>
{% if c.anonymous %}<p class="muted">The pilgrim chose to stay anonymous. They cannot be contacted.</p>
{% elif can_msg %}
<form method="post" action="{{ url_for('admin.complaint_message', ref=c.ref) }}">
<input type="hidden" name="csrf_token" value="{{ csrf() }}">
<label>Send a WhatsApp message (you will not see the number)</label>
<textarea name="text" maxlength="800" placeholder="Type your reply to the pilgrim"></textarea>
<div class="actions" style="margin-top:8px"><button type="submit">📨 Send on WhatsApp</button></div></form>
<p class="muted">WhatsApp only allows this within 24 hours after the pilgrim's last message. If the pilgrim answers, the bot will reply to them normally; the answer does not appear here.</p>
{% if can_reveal %}<form method="post" action="{{ url_for('admin.complaint_reveal', ref=c.ref) }}" style="margin-top:8px"><input type="hidden" name="csrf_token" value="{{ csrf() }}"><button type="submit" class="danger">📞 Show number to call (recorded in the audit log)</button></form>{% endif %}
{% else %}<p class="muted">No contact number is stored for this pilgrim (contact storage is off, or the report was filed before it was enabled).</p>{% endif %}</div>

<div class="panel" style="margin-top:12px"><h3>Timeline</h3><ul class="timeline">
{% for e in events %}<li><b>{{ e.event|replace('_', ' ')|capitalize }}</b> <small>{{ e.when }} · {{ e.who }}</small>{% if e.note %}<div>{{ e.note }}</div>{% endif %}</li>
{% else %}<li class="muted">No events yet.</li>{% endfor %}</ul></div>
{% endblock %}"""

T["feedback.html"] = r"""{% extends "base.html" %}
{% block title %}Feedback{% endblock %}
{% block content %}
<h1>⭐ Feedback</h1>
<section class="cards">
<div class="card"><div class="k">Answers rated</div><div class="v">{{ total }}</div><div class="s">newest 500</div></div>
<div class="card"><div class="k">Question solved</div><div class="v">{{ (pct ~ '%') if pct is not none else '–' }}</div></div>
<div class="card"><div class="k">Average rating</div><div class="v">{{ avg if avg is not none else '–' }}</div><div class="s">out of 5</div></div>
</section>
<div class="panel"><h3>Ratings</h3><div class="bars">
{% for star, n in dist %}<div><span style="width:44px">{{ star }} ⭐</span><i style="width:{{ (n * 10) if n < 30 else 300 }}px"></i><span>{{ n }}</span></div>{% endfor %}
</div></div>
<div class="panel scroll" style="margin-top:12px"><h3>Not solved (each one also appears under Complaints)</h3><table>
<thead><tr><th>Time</th><th>Pilgrim</th><th>Last question</th><th>Problem written</th></tr></thead><tbody>
{% for r in bad %}<tr><td>{{ r.when }}</td><td>{{ r.code }}</td><td class="q">{{ r.q }}</td><td class="q">{{ r.p }}</td></tr>
{% else %}<tr><td colspan="4" class="muted">Nothing here. 🙏</td></tr>{% endfor %}
</tbody></table></div>
{% endblock %}"""


@bp.route("/static/extra.js")
def asset_extra_js():
    r = make_response(EXTRA_JS)
    r.headers["Content-Type"] = "application/javascript; charset=utf-8"
    return r


# Plug the new look and pages into admin.py (runs once, before the first page is shown)
A.CSS = A.CSS + EXTRA_CSS
A.TEMPLATES["base.html"] = NEW_BASE
A.TEMPLATES["dashboard.html"] = A.TEMPLATES["dashboard.html"].replace(
    '<section class="cards">', EXTRA_CARDS + '<section class="cards">', 1)
A.TEMPLATES.update(T)
