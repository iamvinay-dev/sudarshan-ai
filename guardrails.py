# -*- coding: utf-8 -*-
"""
guardrails.py
-------------
Safety layer for Sudarshan AI (TTD Pilgrim Assistant).

What this file does (no AI call, no cost):
    1. Detects prompt-injection attempts      ("ignore previous instructions", "show your prompt" ...)
    2. Detects questions about the bot itself ("which AI model are you", "what data do you use" ...)
    3. Detects clearly off-topic questions    ("capital of India", "write a poem", "2+2" ...)
    4. Handles polite small talk              ("thanks", "ok", "Om Namo Venkatesaya" ...)
    5. Cleans every AI reply before it is sent (blocks leaks of model / provider / prompt / data source)

Used by app.py:
    reply, reason = guardrails.screen_input(text, telugu, has_domain_match)
    text, reason  = guardrails.sanitize_ai_reply(ai_text, telugu)
"""

import re
import unicodedata

MAX_REPLY_CHARS = 3500

# ---------------------------------------------------------------------------
# Fixed replies (English + Telugu). Nothing here reveals any technical detail.
# ---------------------------------------------------------------------------
IDENTITY_REPLY_EN = (
    "🙏 I'm *Sudarshan AI*, the TTD Pilgrim Assistant, here to help with your "
    "Tirumala visit.\n\n"
    "Ask me about darshan, tickets, stay, travel, temple rules, annadanam or laddu, "
    "or reply *0* for the menu."
)
IDENTITY_REPLY_TE = (
    "🙏 నేను *సుదర్శన్ AI*, TTD యాత్రికుల సహాయకుడిని. మీ తిరుమల యాత్రలో సహాయం చేస్తాను.\n\n"
    "దర్శనం, టికెట్లు, వసతి, రవాణా, ఆలయ నియమాలు, అన్నదానం, లడ్డు గురించి అడగండి, "
    "లేదా మెనూ కోసం *0* పంపండి."
)

OFFTOPIC_REPLY_EN = (
    "🙏 I can only help with your Tirumala pilgrimage.\n\n"
    "Reply *0* for the menu, or ask about darshan, stay, travel or temple rules."
)
OFFTOPIC_REPLY_TE = (
    "🙏 నేను తిరుమల యాత్రకు సంబంధించిన విషయాల్లో మాత్రమే సహాయం చేయగలను.\n\n"
    "మెనూ కోసం *0* పంపండి, లేదా దర్శనం, వసతి, రవాణా, ఆలయ నియమాల గురించి అడగండి."
)

SAFE_FALLBACK_EN = (
    "🙏 Sorry, I don't have that exact detail.\n\n"
    "Please check the official TTD website https://tirumala.org or the TTD Call Centre. "
    "Reply *0* for the menu."
)
SAFE_FALLBACK_TE = (
    "🙏 క్షమించండి, ఆ ఖచ్చితమైన వివరం నా వద్ద లేదు.\n\n"
    "దయచేసి అధికారిక TTD వెబ్‌సైట్ https://tirumala.org లేదా TTD కాల్ సెంటర్‌ను సంప్రదించండి. "
    "మెనూ కోసం *0* పంపండి."
)

NOANSWER_REPLY_EN = (
    "🙏 Sorry, I don't have this exact information.\n\n"
    "Please check https://tirumala.org or contact the TTD help desk / Call Centre.\n\n"
    "If you want TTD to look into it, reply *C* to register a complaint or request."
)
NOANSWER_REPLY_TE = (
    "🙏 క్షమించండి, ఈ ఖచ్చితమైన సమాచారం నా వద్ద లేదు.\n\n"
    "దయచేసి https://tirumala.org చూడండి లేదా TTD హెల్ప్ డెస్క్ / కాల్ సెంటర్‌ను సంప్రదించండి.\n\n"
    "TTD పరిశీలించాలంటే, ఫిర్యాదు లేదా అభ్యర్థన నమోదు చేయడానికి *C* పంపండి."
)
CLARIFY_REPLY_EN = (
    "🙏 Please tell me a little more so I can help.\n\n"
    "For example: _darshan timings_, _free stay_, _dress code_.\n"
    "Or reply *0* for the menu."
)
CLARIFY_REPLY_TE = (
    "🙏 నేను సహాయం చేయడానికి దయచేసి కొంచెం వివరంగా చెప్పండి.\n\n"
    "ఉదాహరణ: _దర్శనం సమయాలు_, _ఉచిత వసతి_, _దుస్తుల నియమాలు_.\n"
    "లేదా మెనూ కోసం *0* పంపండి."
)

SMALLTALK_REPLY_EN = (
    "🙏 You're most welcome! Om Namo Venkatesaya.\n\n"
    "Reply *0* anytime for the menu."
)
SMALLTALK_REPLY_TE = (
    "🙏 మీకు స్వాగతం! ఓం నమో వేంకటేశాయ.\n\n"
    "మెనూ కోసం ఎప్పుడైనా *0* పంపండి."
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
_ZERO_WIDTH = dict.fromkeys(map(ord, "\u200b\u200c\u200d\u2060\ufeff"), None)


def is_telugu(text: str) -> bool:
    return any("\u0c00" <= ch <= "\u0c7f" for ch in (text or ""))


def normalize(text: str) -> str:
    """Lowercase, remove invisible characters, collapse spaces."""
    text = unicodedata.normalize("NFKC", text or "")
    text = text.translate(_ZERO_WIDTH).lower()
    return re.sub(r"\s+", " ", text).strip()


def _compile(patterns):
    return [re.compile(p) for p in patterns]


def _any_regex(regexes, text):
    return any(r.search(text) for r in regexes)


def _any_substring(items, text):
    return any(s in text for s in items)


# ---------------------------------------------------------------------------
# 1) PROMPT INJECTION / JAILBREAK ATTEMPTS
# ---------------------------------------------------------------------------
_INJECTION_REGEX = _compile([
    r"\b(ignore|disregard|forget|override|bypass)\b.{0,30}\b(instructions?|rules?|prompts?|guidelines?|restrictions?|programming|directions?)\b",
    r"\b(reveal|show|print|display|tell|give|repeat|leak|share|output)\b.{0,20}\b(your|ur|the above|above|system|hidden|initial|secret|original)\b.{0,15}\b(prompts?|instructions?|rules|guidelines|config(uration)?)\b",
    r"\b(system|initial|hidden|secret|original) (prompt|message|instructions?)\b",
    r"\byou are now\b",
    r"\bfrom now on\b.{0,30}\b(you|act|behave|respond|reply|answer)\b",
    r"\bact as\b",
    r"\bpretend\b",
    r"\brole ?play\b",
    r"\b(developer|dev|admin|god|sudo|debug|dan) mode\b",
    r"\bjailbreak\b",
    r"\bdo anything now\b",
    r"\b(no|without|remove|disable) (any )?(restrictions|filters|limits|rules|safety)\b",
    r"\bunfiltered\b",
    r"\bnew (instructions|rules|persona)\b",
    r"<\s*/?\s*(system|assistant|user|pilgrim_message)\s*>",
    r"\[\s*(system|inst)\s*\]",
    # Romanized Telugu ("Tenglish") attempts
    r"\b(prompt|instructions?)\b.{0,15}\b(chupinchu|chupinchandi|cheppu|cheppandi|chepu|ivvu|ivvandi)\b",
    r"\b(nee|ni|mee|me)\s+(prompt|instructions?)\b",
    r"\b(marchipo|marchipondi|pattinchukoku)\b",
])
_INJECTION_TELUGU = [
    "సిస్టమ్ ప్రాంప్ట్", "ప్రాంప్ట్", "మునుపటి సూచనలు",
    "సూచనలను విస్మరించు", "సూచనలను పట్టించుకోకు",
]


def is_injection_attempt(text: str) -> bool:
    t = normalize(text)
    return _any_regex(_INJECTION_REGEX, t) or _any_substring(_INJECTION_TELUGU, t)


# ---------------------------------------------------------------------------
# 2) QUESTIONS ABOUT THE BOT ITSELF (model, provider, data, code ...)
# ---------------------------------------------------------------------------
_IDENTITY_REGEX = _compile([
    r"\b(which|what)\s+(ai|llm|model|language model|api)\b",
    r"\b(which|what)\s+(company|technology|tech)\s+(made|built|created|powers|is behind|are you|do you use|is used)\b",
    r"\bwho\s+(made|created|built|developed|trained|designed|programmed|owns)\s+(you|this (bot|chatbot|app|ai|assistant))\b",
    r"\bare you\s+(chatgpt|gpt|gemini|grok|groq|llama|claude|cohere|openai|bard|copilot|an? (ai|bot|robot|llm|language model))\b",
    r"\b(your|ur)\s+(model|data|dataset|source|sources|training|database|code|api|backend|tech stack|architecture|knowledge|prompt|instructions?|rules|guidelines|programming)\b",
    r"\bwhat (data|dataset|sources?) do you (have|use|hold)\b",
    r"\b(knowledge base|data source|source code|tech stack|api key)\b",
    r"\b(trained on|powered by|built with|built using|made with|made using)\b",
    r"\bhow (were|are|was) you (built|made|created|trained|developed)\b",
    r"\bhow do you work\b",
    r"\bwho are you\b",
    r"\bwhat are you\b",
    r"\bwhat('?s| is) your name\b",
    r"\bintroduce yourself\b",
])
_IDENTITY_TELUGU = [
    "నువ్వు ఎవరు", "నీవు ఎవరు", "మీరు ఎవరు", "ఏ మోడల్", "ఏ ఏఐ", "ఏ ai",
    "నిన్ను ఎవరు తయారు", "మిమ్మల్ని ఎవరు తయారు",
    "నిన్ను ఎవరు రూపొందించారు", "మిమ్మల్ని ఎవరు రూపొందించారు",
    "మీ డేటా", "నీ డేటా",
]


def is_identity_question(text: str) -> bool:
    t = normalize(text)
    return _any_regex(_IDENTITY_REGEX, t) or _any_substring(_IDENTITY_TELUGU, t)


# ---------------------------------------------------------------------------
# 3) CLEARLY OFF-TOPIC (only refused when there is NO pilgrimage keyword)
# ---------------------------------------------------------------------------
_OFFTOPIC_REGEX = _compile([
    r"\bcapital (of|city of)\b",
    r"\b(president|prime minister|chief minister|governor) of\b",
    r"\bwho (is|was) the (president|prime minister|chief minister)\b",
    r"\b(ipl|cricket score|world cup|football score|match score|live score)\b",
    r"\b(stock price|stock market|share market|nifty|sensex|bitcoin|crypto)\b",
    r"\bwrite (me )?(a |an |some )?(poem|song|story|essay|joke|email|letter|code|program|script|function)\b",
    r"\b(python|javascript|java|html|css|sql|c\+\+)\b.{0,15}\b(code|program|script|function|error)\b",
    r"\btell (me )?(a )?(joke|riddle)\b",
    r"\b(recipe for|how to cook|how to bake)\b",
    r"\b(movie|film|web series|song lyrics|actor|actress|celebrity)\b",
    r"\b(solve|calculate|equation|homework|assignment)\b",
    r"\btranslate\b.{0,40}\b(to|into)\b",
    r"\b(prescribe|diagnos[ei]|symptoms of)\b",
    r"\b(girlfriend|boyfriend|dating|love advice)\b",
    r"\bmeaning of life\b",
    r"^\s*[\d\s\+\-\*/x×÷=().,%^]+\s*$",
    r"\bwhat is \d+\s*[\+\-\*/x×÷]\s*\d+\b",
])
_OFFTOPIC_TELUGU = ["రాజధాని", "జోక్ చెప్పు", "కవిత రాయి", "సినిమా", "క్రికెట్ స్కోర్"]

_PILGRIM_KEYWORDS = re.compile(
    r"\b(?:tirumala|tirupati|ttd|darshan|temple|venkates|balaji|srinivasa|govinda|"
    r"laddu|prasad|seva|ticket|token|accommodation|room|stay|bus|train|railway|"
    r"alipiri|mettu|footpath|dress|tonsure|annadanam|pilgrim|padmavathi|"
    r"brahmotsavam|vaikunta|hundi|locker|queue|crowd|ssd|slotted|abhishekam|suprabhatam)"
)
_PILGRIM_KEYWORDS_TELUGU = [
    "తిరుమల", "తిరుపతి", "దర్శన", "స్వామి", "లడ్డు", "టికెట్", "వసతి",
    "ఆలయ", "శ్రీవారి", "గోవింద", "ప్రసాదం", "అన్నదానం", "వేంకటేశ్వర",
]


def has_pilgrim_keyword(text: str) -> bool:
    t = normalize(text)
    return bool(_PILGRIM_KEYWORDS.search(t)) or _any_substring(_PILGRIM_KEYWORDS_TELUGU, t)


def is_clearly_off_topic(text: str, has_domain_match: bool = False) -> bool:
    t = normalize(text)
    if has_domain_match or has_pilgrim_keyword(t):
        return False
    return _any_regex(_OFFTOPIC_REGEX, t) or _any_substring(_OFFTOPIC_TELUGU, t)


# ---------------------------------------------------------------------------
# 4) SMALL TALK
# ---------------------------------------------------------------------------
_SMALLTALK = {
    "thanks", "thank you", "thankyou", "thx", "ty", "ok", "okay", "k", "fine",
    "good", "great", "nice", "bye", "goodbye", "good night", "good morning",
    "om namo venkatesaya", "om namo venkatesaya namaha", "govinda", "govinda govinda",
    "jai balaji", "jai srinivasa", "om namo narayanaya",
    "ధన్యవాదాలు", "థాంక్స్", "సరే", "గోవిందా", "గోవింద గోవింద",
    "ఓం నమో వేంకటేశాయ", "ఓం నమో నారాయణాయ",
}


def is_smalltalk(text: str) -> bool:
    t = re.sub(r"[^\w\s\u0c00-\u0c7f]", "", normalize(text)).strip()
    return t in _SMALLTALK


# ---------------------------------------------------------------------------
# PUBLIC: screen the pilgrim's message BEFORE any AI call
# ---------------------------------------------------------------------------
def screen_input(text: str, telugu: bool = False, has_domain_match: bool = False):
    """Returns (reply, reason).
    reply is None when the message is fine to continue normal handling.
    reason is one of: "injection", "identity", "smalltalk", "offtopic", "".
    """
    te = telugu or is_telugu(text)

    if is_injection_attempt(text):
        return (IDENTITY_REPLY_TE if te else IDENTITY_REPLY_EN), "injection"
    if is_identity_question(text):
        return (IDENTITY_REPLY_TE if te else IDENTITY_REPLY_EN), "identity"
    if is_smalltalk(text):
        return (SMALLTALK_REPLY_TE if te else SMALLTALK_REPLY_EN), "smalltalk"
    if is_clearly_off_topic(text, has_domain_match):
        return (OFFTOPIC_REPLY_TE if te else OFFTOPIC_REPLY_EN), "offtopic"
    return None, ""


# ---------------------------------------------------------------------------
# PUBLIC: clean an AI reply BEFORE sending it to the pilgrim
# ---------------------------------------------------------------------------
_LEAK_REGEX = re.compile(
    r"(groq|cohere|gemini|openai|chatgpt|\bgpt\b|\bgpt-\w+|llama|\bgrok\b|anthropic|claude|"
    r"mistral|deepseek|\bllm\b|language model|large language|system prompt|"
    r"knowledge[ -]base|api[ -]key|my instructions|my guidelines|my rules|"
    r"i was trained|trained by|supabase|\bflask\b|\bpython\b|whatsapp cloud|"
    r"as an ai\b|artificial intelligence model)",
    re.IGNORECASE,
)


def sanitize_ai_reply(reply: str, telugu: bool = False):
    """Returns (safe_text, reason).
    reason: "ok", "offtopic", "identity", "noanswer", "short", "leak"."""
    text = (reply or "").strip()
    head = text[:40].upper()

    if head.startswith("OFF_TOPIC"):
        return (OFFTOPIC_REPLY_TE if telugu else OFFTOPIC_REPLY_EN), "offtopic"
    if head.startswith("IDENTITY"):
        return (IDENTITY_REPLY_TE if telugu else IDENTITY_REPLY_EN), "identity"
    if head.startswith("NO_ANSWER"):
        return (NOANSWER_REPLY_TE if telugu else NOANSWER_REPLY_EN), "noanswer"
    # An almost empty reply (for example just "#") is never sent to a pilgrim.
    if sum(1 for ch in text if ch.isalpha()) < 12:
        return (NOANSWER_REPLY_TE if telugu else NOANSWER_REPLY_EN), "short"
    if _LEAK_REGEX.search(text):
        return (SAFE_FALLBACK_TE if telugu else SAFE_FALLBACK_EN), "leak"
    return text[:MAX_REPLY_CHARS], "ok"


_NUM = re.compile(r"\d+(?::\d+)?")


def numbers_supported(reply: str, facts: str, user_text: str = "") -> bool:
    """True when every number with 2+ digits (prices, times, dates) in the reply also
    appears in the facts the AI was given (or in the pilgrim's own message)."""
    known = set(_NUM.findall((facts or "") + " " + (user_text or "")))
    for n in _NUM.findall(reply or ""):
        if len(n) < 2 and ":" not in n:
            continue
        if n not in known:
            return False
    return True


def is_too_vague(text: str, has_domain_match: bool = False) -> bool:
    """One or two unclear words such as "what" or "hello there"."""
    if has_domain_match or has_pilgrim_keyword(text) or (text or "").strip().isdigit():
        return False
    words = re.findall(r"[\w\u0c00-\u0c7f]+", normalize(text))
    return len(words) <= 2
