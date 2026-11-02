# -*- coding: utf-8 -*-
"""
quick_help.py
-------------
Extra answers for Sudarshan AI. Does NOT change app.py logic; app.py just calls
quick_help.find_reply(...) once (see the 3-line change at the bottom of this file).

Handles
  1. Several topics in ONE message  ("darshan timings and accommodation")
     -> answers each topic from the existing knowledge base (no invented facts).
  2. "How do I reach Tirupati from Bangalore?"
     -> short, simple travel answer for that city.
  3. "How do I reach Tirupati?" (no city)
     -> asks the reverse question: "Which city are you travelling from?"
        and answers on the next message.
"""

import re
import time

from knowledge_base import search_relevant_qas, format_direct_answer

# ---------------------------------------------------------------------------
# 1) Multi-topic questions
# ---------------------------------------------------------------------------
# topic name -> (words that trigger it, query sent to the knowledge base)
TOPICS = {
    "darshan": ({"darshan", "darshanam", "timings", "timing", "దర్శనం", "దర్శన"},
                "darshan timings"),
    "accommodation": ({"accommodation", "room", "rooms", "stay", "lodging", "hotel",
                       "cottage", "వసతి", "గది", "గదులు"},
                      "accommodation rooms booking"),
}


def _words(text):
    return set(re.findall(r"[a-z']+", text.lower()))


def _topic_hit(trigger, text, words):
    return any((t in words) if re.fullmatch(r"[a-z']+", t) else (t in text) for t in trigger)


def _multi_topic(work, te):
    low, words = work.lower(), _words(work)
    found = [name for name, (trig, _) in TOPICS.items() if _topic_hit(trig, low, words)]
    if len(found) < 2:                      # only act when 2+ topics are asked together
        return None
    parts = []
    for name in found:
        top = search_relevant_qas(TOPICS[name][1], top_n=1)
        if top:
            parts.append(format_direct_answer(top[0], telugu=te))
    if len(parts) < 2:                      # not enough facts -> let the normal pipeline handle it
        return None
    return {"reply": "\n\n➖➖➖\n\n".join(parts), "topic": "+".join(found)}


# ---------------------------------------------------------------------------
# 2) / 3) How to reach Tirupati
# ---------------------------------------------------------------------------
REACH_RE = re.compile(
    r"(how\s+(do|can|to|should)\s+(i|we)?\s*(reach|go|get|travel)|how\s+to\s+(reach|go|get)|"
    r"\b(route|way to|reach|travel to|journey|directions?)\b|ఎలా వెళ్ళాలి|ఎలా చేరుకోవాలి|చేరుకోవడం)",
    re.I)
PLACE_RE = re.compile(r"(tirupati|tirumala|tirupathi|tirpati|తిరుపతి|తిరుమల)", re.I)

CITIES = {
    "bangalore": ["bangalore", "bengaluru", "bnglr", "blr", "banglore", "బెంగళూరు"],
    "chennai":   ["chennai", "madras", "చెన్నై"],
    "hyderabad": ["hyderabad", "hyd", "secunderabad", "హైదరాబాద్"],
}

TRAVEL = {
    "bangalore": (
        "🚌 *Bangalore → Tirupati* (about 250 km, roughly 5–6 hours)\n"
        "• 🚆 *Train:* direct trains run from Bangalore to Tirupati - check IRCTC for timings.\n"
        "• 🚌 *Bus:* APSRTC and KSRTC buses leave from Majestic (Kempegowda) bus stand.\n"
        "• 🚗 *Car:* via Hosur - Krishnagiri - Chittoor, or via Kolar - Chittoor.\n"
        "• ✈️ *Flight:* Bangalore to Tirupati airport.\n\n"
        "Then from Tirupati to Tirumala (about 22 km): APSRTC buses, taxis, or walk the "
        "Alipiri / Srivari Mettu footpath. 🙏"),
    "chennai": (
        "🚌 *Chennai → Tirupati* (about 135-150 km, roughly 3 hours)\n"
        "• 🚆 *Train:* many trains daily from Chennai Central - check IRCTC.\n"
        "• 🚌 *Bus:* frequent APSRTC / TNSTC buses from Koyambedu (CMBT).\n"
        "• 🚗 *Car:* via Chennai-Kolkata highway (NH16) and Renigunta road.\n\n"
        "Then from Tirupati to Tirumala (about 22 km): buses, taxis, or the Alipiri footpath. 🙏"),
    "hyderabad": (
        "🚌 *Hyderabad → Tirupati* (about 550-600 km, 9-10 hours by road)\n"
        "• 🚆 *Train:* direct trains from Secunderabad / Kacheguda - check IRCTC.\n"
        "• 🚌 *Bus:* APSRTC / TGSRTC buses from MGBS / JBS.\n"
        "• ✈️ *Flight:* Hyderabad to Tirupati airport (about 1 hour).\n\n"
        "Then from Tirupati to Tirumala (about 22 km): buses, taxis, or the Alipiri footpath. 🙏"),
}
TRAVEL_OTHER = (
    "🚌 *Reaching Tirupati*\n"
    "• 🚆 *Train:* Tirupati and Renigunta stations connect to most major cities.\n"
    "• 🚌 *Bus:* APSRTC and other state buses reach Tirupati bus stand.\n"
    "• ✈️ *Flight:* Tirupati airport (Renigunta) has flights from several cities.\n\n"
    "Then from Tirupati to Tirumala (about 22 km): buses, taxis, or the Alipiri / Srivari Mettu "
    "footpath. 🙏\n\nTell me your city for more specific help.")
TRAVEL_TE = (
    "🚌 *తిరుపతికి చేరుకోవడం*\n"
    "• 🚆 రైలు: తిరుపతి, రేణిగుంట స్టేషన్లు ముఖ్య నగరాలతో అనుసంధానమై ఉన్నాయి.\n"
    "• 🚌 బస్సు: APSRTC బస్సులు తిరుపతి బస్టాండ్‌కు వస్తాయి.\n"
    "• ✈️ విమానం: తిరుపతి విమానాశ్రయం (రేణిగుంట).\n\n"
    "తిరుపతి నుండి తిరుమలకు (సుమారు 22 కి.మీ) బస్సులు, ట్యాక్సీలు లేదా అలిపిరి నడక మార్గం "
    "ఉన్నాయి. 🙏\n\nమీ నగరం చెప్పండి, మరింత వివరంగా చెబుతాను.")
ASK_CITY_EN = "🙏 Sure! Which city are you travelling from? (for example: Bangalore, Chennai, Hyderabad)"
ASK_CITY_TE = "🙏 తప్పకుండా! మీరు ఏ నగరం నుండి వస్తున్నారు? (ఉదా: బెంగళూరు, చెన్నై, హైదరాబాద్)"

_pending = {}          # phone -> time we asked "which city?"   (kept in RAM, 10 minute memory)
PENDING_SECONDS = 600


def _find_city(text):
    low = text.lower()
    words = _words(text)
    for city, names in CITIES.items():
        for n in names:
            if (n in words) if re.fullmatch(r"[a-z]+", n) else (n in low):
                return city
    return None


def _travel_reply(city, te):
    if te:
        return TRAVEL_TE
    return TRAVEL.get(city, TRAVEL_OTHER)


def _reach(phone, work, te):
    city = _find_city(work)
    asked_recently = time.time() - _pending.get(phone, 0) < PENDING_SECONDS

    # Pilgrim is answering our "which city?" question
    if asked_recently and len(work.split()) <= 4 and not REACH_RE.search(work):
        _pending.pop(phone, None)
        return {"reply": _travel_reply(city, te), "topic": "travel"}

    if PLACE_RE.search(work) and REACH_RE.search(work):
        if city:
            _pending.pop(phone, None)
            return {"reply": _travel_reply(city, te), "topic": "travel"}
        _pending[phone] = time.time()
        return {"reply": ASK_CITY_TE if te else ASK_CITY_EN, "topic": "travel"}

    # "from Bangalore to Tirupati" without a reach word
    if city and PLACE_RE.search(work) and re.search(r"\bfrom\b|నుండి|నుంచి", work.lower()):
        return {"reply": _travel_reply(city, te), "topic": "travel"}
    return None


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------
def find_reply(phone, work, te):
    """Returns {"reply": text, "topic": name} or None (then app.py continues as usual)."""
    return _reach(phone, work, te) or _multi_topic(work, te)


# ---------------------------------------------------------------------------
# HOW TO PLUG IT INTO app.py  (only 2 small additions, nothing rewritten)
# ---------------------------------------------------------------------------
# A) With the other imports at the top of app.py add:
#
#       import quick_help
#
# B) In _core(), right AFTER the "# 5) live notices" block and BEFORE
#    "# 6) direct knowledge-base match", add:
#
#       quick = quick_help.find_reply(phone, work, te)
#       if quick:
#           return quick["reply"], _meta("quick", category=quick["topic"],
#                                        matched=quick["topic"], topic=quick["topic"])
