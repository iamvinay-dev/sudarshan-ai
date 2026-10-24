# -*- coding: utf-8 -*-
"""
complaints.py
-------------
Complaint, bribe-report and feedback conversations on WhatsApp (no AI is used here).

Complaint flow : pilgrim writes "complaint" / "bribe" / "లంచం" ... -> category -> details
                 -> (bribe only) anonymous? -> reference like C-1042 is returned.
Feedback flow  : "Was your question solved? Y / N" -> rating 1-5, or the problem text.
                 A "not solved" problem also becomes a complaint (category "unsolved").

Privacy:
  * Text is redacted (phone numbers, e-mails, ID-like strings) before saving.
  * The pilgrim's number is saved ENCRYPTED (db.encrypt_phone) only when the pilgrim
    did not choose "anonymous", and only if PHONE_ENC_SECRET is set.
  * Complaint text is never sent to an AI model.

All functions return plain text. The conversation state lives in memory (it is only
needed for a few minutes).
"""

import re
import time
import logging

import db

log = logging.getLogger("sudarshan-ai.complaints")

STATE_TTL = 15 * 60
MAX_STATES = 3000
_state = {}

CATEGORIES = {"1": "darshan", "2": "accommodation", "3": "transport",
              "4": "staff", "5": "bribe", "6": "other"}

_COMPLAINT_RE = re.compile(
    r"\b(complain\w*|grievance|cheat\w*|bribe\w*|corrupt\w*|extra money|"
    r"(?:asked|demanded|took|taking)\s+(?:for\s+)?(?:extra\s+)?money|overcharg\w*|"
    r"rude|misbehav\w*|harass\w*|fraud|scam|black ?market|lancham|firyadu)\b")
_COMPLAINT_TE = ["ఫిర్యాదు", "లంచం", "డబ్బులు అడిగ", "మోసం", "దురుసు", "వేధ", "అక్రమ"]
_BRIBE_RE = re.compile(r"\b(bribe\w*|corrupt\w*|extra money|(?:asked|demanded|took)\s+(?:for\s+)?(?:extra\s+)?money|lancham)\b")
_BRIBE_TE = ["లంచం", "డబ్బులు అడిగ"]

_YES = {"y", "yes", "yeah", "yep", "avunu", "అవును", "1"}
_NO = {"n", "no", "nope", "ledu", "కాదు", "లేదు", "2"}


def _t(en, te, telugu):
    return te if telugu else en


# ---------------------------------------------------------------------------
# Intent detection
# ---------------------------------------------------------------------------
def detect_intent(text: str):
    """Returns None, "complaint" or "bribe"."""
    t = (text or "").strip().lower()
    if t in ("c", "complaint"):
        return "complaint"
    if _BRIBE_RE.search(t) or any(w in t for w in _BRIBE_TE):
        return "bribe"
    if _COMPLAINT_RE.search(t) or any(w in t for w in _COMPLAINT_TE):
        return "complaint"
    return None


# ---------------------------------------------------------------------------
# State helpers
# ---------------------------------------------------------------------------
def _get(phone):
    s = _state.get(phone)
    if s and time.time() - s["ts"] > STATE_TTL:
        _state.pop(phone, None)
        return None
    return s


def _set(phone, step, **data):
    _state[phone] = {"step": step, "ts": time.time(), "data": data}
    while len(_state) > MAX_STATES:
        _state.pop(next(iter(_state)))


def clear(phone):
    _state.pop(phone, None)


def in_flow(phone) -> bool:
    return _get(phone) is not None


# ---------------------------------------------------------------------------
# Saving
# ---------------------------------------------------------------------------
def create_complaint(phone, lang, category, details, anonymous, last_question=None, source="complaint"):
    """Save a complaint. Returns the reference (for example 'C-1042') or None."""
    if not db.logging_enabled():
        return None
    pid = db._pilgrim_id(phone, lang)
    if pid is None:
        return None
    if not anonymous and db.contact_enabled():
        try:
            db._request("PATCH", "pilgrims", params={"id": f"eq.{pid}"},
                        body={"phone_enc": db.encrypt_phone(phone)}, prefer="return=minimal")
        except Exception as exc:  # noqa: BLE001
            log.error("Could not store the contact number: %s", type(exc).__name__)
    row = {
        "pilgrim_id": pid, "category": category, "is_bribe": category == "bribe",
        "anonymous": bool(anonymous), "language": lang,
        "details": db.redact(details)[:1000],
        "last_question": db.redact(last_question or "")[:300] or None, "source": source,
    }
    rows = db._json(db._request("POST", "complaints", body=row, prefer="return=representation"))
    if not rows:
        return None
    c = rows[0]
    db._request("POST", "complaint_events", body={"complaint_id": c["id"], "event": "created", "note": source},
                prefer="return=minimal")
    return c.get("ref")


def _done_text(ref, anonymous, telugu):
    contact_en = ("Your report is anonymous." if anonymous
                  else "TTD may reply to you here on WhatsApp.")
    contact_te = ("మీ ఫిర్యాదు అజ్ఞాతంగా ఉంటుంది." if anonymous
                  else "TTD మీకు ఇదే WhatsApp లో సమాధానం ఇవ్వవచ్చు.")
    return _t(
        f"✅ *Your complaint is registered.*\n\n📌 Reference: *{ref}*\n"
        f"⏰ TTD will review it within 24 hours.\n{contact_en}\n\nReply *0* for the menu.",
        f"✅ *మీ ఫిర్యాదు నమోదు అయింది.*\n\n📌 రిఫరెన్స్: *{ref}*\n"
        f"⏰ TTD 24 గంటల్లో పరిశీలిస్తుంది.\n{contact_te}\n\nమెనూ కోసం *0* పంపండి.", telugu)


def _failed_text(telugu):
    return _t("🙏 Sorry, I could not save your complaint right now. Please try again in a few minutes "
              "or contact the TTD Call Centre.",
              "🙏 క్షమించండి, ఇప్పుడు మీ ఫిర్యాదును సేవ్ చేయలేకపోయాను. కొద్ది నిమిషాల తర్వాత మళ్లీ ప్రయత్నించండి "
              "లేదా TTD కాల్ సెంటర్‌ను సంప్రదించండి.", telugu)


# ---------------------------------------------------------------------------
# Starting flows
# ---------------------------------------------------------------------------
def _category_menu(telugu):
    return _t(
        "📝 *Register a complaint*\n\nWhat is it about? Reply with a number:\n\n"
        "*1* 🎟️ Darshan / queue\n*2* 🏨 Accommodation\n*3* 🚌 Transport\n"
        "*4* 👤 Staff behaviour\n*5* 🚫 Bribe / corruption\n*6* 📋 Other\n\n"
        "Reply *cancel* to stop.",
        "📝 *ఫిర్యాదు నమోదు*\n\nఏ విషయం గురించి? ఒక నంబర్ పంపండి:\n\n"
        "*1* 🎟️ దర్శనం / క్యూ\n*2* 🏨 వసతి\n*3* 🚌 రవాణా\n"
        "*4* 👤 సిబ్బంది ప్రవర్తన\n*5* 🚫 లంచం / అవినీతి\n*6* 📋 ఇతర\n\n"
        "ఆపడానికి *cancel* పంపండి.", telugu)


def _details_prompt(category, telugu):
    if category == "bribe":
        return _t("🚫 *Bribe / corruption report*\n\nPlease type what happened: where, when, and who "
                  "(a name or description if you know it). Do not share Aadhaar or card numbers.",
                  "🚫 *లంచం / అవినీతి నివేదిక*\n\nఏమి జరిగిందో టైప్ చేయండి: ఎక్కడ, ఎప్పుడు, ఎవరు "
                  "(తెలిస్తే పేరు లేదా వివరణ). ఆధార్ లేదా కార్డ్ నంబర్లు పంపవద్దు.", telugu)
    return _t("✍️ Please type your complaint with as much detail as you can (place, time, what happened). "
              "Do not share Aadhaar or card numbers.",
              "✍️ మీ ఫిర్యాదును వివరంగా టైప్ చేయండి (ప్రదేశం, సమయం, ఏమి జరిగింది). "
              "ఆధార్ లేదా కార్డ్ నంబర్లు పంపవద్దు.", telugu)


def start_complaint(phone, telugu, intent="complaint", last_question=None):
    """Returns the first reply of the complaint flow."""
    if intent == "bribe":
        _set(phone, "details", category="bribe", last_question=last_question)
        return _details_prompt("bribe", telugu)
    _set(phone, "cat", tries=0, last_question=last_question)
    return _category_menu(telugu)


def ask_feedback(phone, last_question, category, topic, telugu):
    """Starts the 'was your question solved?' conversation. Returns the text to append."""
    _set(phone, "fb_solved", last_question=last_question, category=category, topic=topic)
    return _t("\n\n━━━━━━━━\n🙏 *Was your question solved?*\nReply *Y* for Yes or *N* for No.",
              "\n\n━━━━━━━━\n🙏 *మీ ప్రశ్నకు సమాధానం దొరికిందా?*\nఅవును అయితే *Y*, కాదు అయితే *N* పంపండి.", telugu)


# ---------------------------------------------------------------------------
# Continuing an active flow.  Returns (reply, source, category) or None.
# None means: "this message is not part of the flow, handle it normally".
# ---------------------------------------------------------------------------
def continue_flow(phone, original, work, telugu, lang):
    s = _get(phone)
    if not s:
        return None
    step, data = s["step"], s["data"]
    low = (work or "").strip().lower()
    raw = (original or "").strip()

    if low in ("cancel", "exit", "stop", "quit", "0", "menu"):
        clear(phone)
        if low in ("0", "menu"):
            return None
        return (_t("Cancelled. Reply *0* for the menu. 🙏", "రద్దు చేయబడింది. మెనూ కోసం *0* పంపండి. 🙏", telugu),
                "complaint", "complaint")

    # ---- complaint: choose category ----
    if step == "cat":
        key = CATEGORIES.get(low)
        if key:
            _set(phone, "details", category=key, last_question=data.get("last_question"))
            return _details_prompt(key, telugu), "complaint", "complaint"
        if len(raw.split()) >= 4:                       # they typed the problem directly
            key = "bribe" if detect_intent(raw) == "bribe" else "other"
            _set(phone, "details", category=key, last_question=data.get("last_question"))
            return _after_details(phone, raw, telugu, lang)
        tries = data.get("tries", 0) + 1
        if tries >= 2:
            clear(phone)
            return None
        _set(phone, "cat", tries=tries, last_question=data.get("last_question"))
        return _category_menu(telugu), "complaint", "complaint"

    # ---- complaint: details ----
    if step == "details":
        if len(raw) < 5:
            return (_t("Please type a little more detail. 🙏", "దయచేసి కొంచెం వివరంగా రాయండి. 🙏", telugu),
                    "complaint", "complaint")
        return _after_details(phone, raw, telugu, lang)

    # ---- bribe: anonymous? ----
    if step == "anon":
        if low in _YES or low in ("anonymous", "అజ్ఞాతం"):
            anonymous = True
        elif low in _NO:
            anonymous = False
        else:
            return (_t("Please reply *1* for Yes (anonymous) or *2* for No.",
                       "అజ్ఞాతంగా ఉండాలంటే *1*, లేకపోతే *2* పంపండి.", telugu), "complaint", "complaint")
        clear(phone)
        ref = create_complaint(phone, lang, "bribe", data.get("details", ""), anonymous,
                               data.get("last_question"))
        return (_done_text(ref, anonymous, telugu) if ref else _failed_text(telugu)), "complaint", "bribe"

    # ---- feedback: solved? ----
    if step == "fb_solved":
        if low in _YES and low != "1":
            _set(phone, "fb_rating", **data)
            return (_t("Great, thank you! 🙏 Please rate this chat from *1* to *5* ⭐ (5 = excellent).",
                       "చాలా సంతోషం! 🙏 ఈ చాట్‌కు *1* నుండి *5* ⭐ వరకు రేటింగ్ ఇవ్వండి (5 = అద్భుతం).", telugu),
                    "feedback", "feedback")
        if low in _NO and low != "2":
            _set(phone, "fb_problem", **data)
            return (_t("I'm sorry about that. 🙏 Please type what went wrong, and TTD will look into it. "
                       "(Type *skip* to skip.)",
                       "క్షమించండి. 🙏 ఏమి సమస్య జరిగిందో టైప్ చేయండి, TTD పరిశీలిస్తుంది. "
                       "(వద్దనుకుంటే *skip* పంపండి.)", telugu), "feedback", "feedback")
        clear(phone)
        return None

    # ---- feedback: rating ----
    if step == "fb_rating":
        if low in ("1", "2", "3", "4", "5"):
            clear(phone)
            db.save_feedback(phone, True, low, data.get("last_question"), data.get("topic"),
                             data.get("category"), lang)
            return (_t("Thank you for your feedback! 🙏 Om Namo Venkatesaya.",
                       "మీ అభిప్రాయానికి ధన్యవాదాలు! 🙏 ఓం నమో వేంకటేశాయ.", telugu), "feedback", "feedback")
        clear(phone)
        return None

    # ---- feedback: problem text ----
    if step == "fb_problem":
        clear(phone)
        if low in ("1", "2", "3", "4", "5", "6", "7"):
            return None
        fid, pid = db.save_feedback(phone, False, None, data.get("last_question"), data.get("topic"),
                                    data.get("category"), lang)
        if low == "skip":
            return (_t("Thank you. 🙏 Reply *0* for the menu.", "ధన్యవాదాలు. 🙏 మెనూ కోసం *0* పంపండి.", telugu),
                    "feedback", "feedback")
        ref = create_complaint(phone, lang, "unsolved", raw, False, data.get("last_question"), source="feedback")
        if ref:
            db.save_problem(fid, pid, phone, raw)
            return _done_text(ref, False, telugu), "feedback", "feedback"
        return _failed_text(telugu), "feedback", "feedback"

    clear(phone)
    return None


def _after_details(phone, raw, telugu, lang):
    s = _get(phone)
    data = s["data"] if s else {}
    category = data.get("category", "other")
    if category == "bribe":
        _set(phone, "anon", details=raw, last_question=data.get("last_question"))
        return (_t("🔒 *Stay anonymous?*\n\nReply *1* for Yes (TTD will not be able to contact you) "
                   "or *2* for No (TTD may contact you here).",
                   "🔒 *అజ్ఞాతంగా ఉండాలా?*\n\nఅవును అయితే *1* (TTD మిమ్మల్ని సంప్రదించలేదు), "
                   "వద్దు అయితే *2* (TTD మీకు ఇక్కడే సమాధానం ఇవ్వవచ్చు).", telugu),
                "complaint", "bribe")
    clear(phone)
    ref = create_complaint(phone, lang, category, raw, False, data.get("last_question"))
    return (_done_text(ref, False, telugu) if ref else _failed_text(telugu)), "complaint", category
