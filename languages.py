# -*- coding: utf-8 -*-
"""
languages.py
------------
Language detection for Sudarshan AI (no AI call, no cost).

detect(text)           -> "en" | "te" | "te-latin" | "hi" | "kn" | "ta" | "ml" | "bn" | "gu" | "or" | "pa" | "ur"
language_switch(text)  -> language code when the pilgrim only types a language name
                          (for example "Kannada" or "reply in Hindi"), else None

"te-latin" means Telugu typed in English letters ("Tenglish"), e.g. "darshanam ela book cheyali".
"""

import re

NAMES = {
    "en": "English", "te": "Telugu", "te-latin": "Telugu", "hi": "Hindi", "kn": "Kannada",
    "ta": "Tamil", "ml": "Malayalam", "bn": "Bengali", "gu": "Gujarati", "or": "Odia",
    "pa": "Punjabi", "ur": "Urdu",
}

# Languages the bot answers by itself (the others are translated).
NATIVE = ("en", "te")

_SCRIPTS = [
    ("te", 0x0C00, 0x0C7F), ("hi", 0x0900, 0x097F), ("bn", 0x0980, 0x09FF),
    ("pa", 0x0A00, 0x0A7F), ("gu", 0x0A80, 0x0AFF), ("or", 0x0B00, 0x0B7F),
    ("ta", 0x0B80, 0x0BFF), ("kn", 0x0C80, 0x0CFF), ("ml", 0x0D00, 0x0D7F),
    ("ur", 0x0600, 0x06FF),
]

_TENGLISH = {
    "ela", "ekkada", "enti", "emiti", "cheppandi", "chepandi", "cheppu", "kavali", "undi",
    "unnayi", "ledu", "avuthundi", "ravali", "vellali", "evaru", "enduku", "eppudu",
    "ippudu", "naaku", "meeru", "nenu", "darshanam", "kaadu", "avunu", "sare",
    "dhanyavadalu", "namaskaram", "bagundi", "cheyali", "cheyyali", "tirumalaku",
    "swamivari", "srivari", "entha", "ekkadundi", "telugulo", "cheppara",
}

_LANG_WORDS = {
    "english": "en", "telugu": "te", "తెలుగు": "te", "hindi": "hi", "हिंदी": "hi", "हिन्दी": "hi",
    "kannada": "kn", "ಕನ್ನಡ": "kn", "tamil": "ta", "தமிழ்": "ta", "malayalam": "ml",
    "മലയാളം": "ml", "bengali": "bn", "bangla": "bn", "বাংলা": "bn", "gujarati": "gu",
    "ગુજરાતી": "gu", "odia": "or", "oriya": "or", "punjabi": "pa", "ਪੰਜਾਬੀ": "pa",
    "urdu": "ur", "اردو": "ur",
}


def detect(text: str) -> str:
    counts, letters = {}, 0
    for ch in text or "":
        if not ch.isalpha() and not ("\u0900" <= ch <= "\u0d7f"):
            continue
        letters += 1
        cp = ord(ch)
        for code, lo, hi in _SCRIPTS:
            if lo <= cp <= hi:
                counts[code] = counts.get(code, 0) + 1
                break
    if counts:
        code, n = max(counts.items(), key=lambda kv: kv[1])
        if n >= 2 or n >= max(1, letters // 3):
            return code
    words = set(re.findall(r"[a-z]+", (text or "").lower()))
    if words & _TENGLISH:
        return "te-latin"
    return "en"


def language_switch(text: str):
    t = re.sub(r"[^\w\s\u0900-\u0d7f\u0600-\u06ff]", " ", (text or "").lower())
    t = re.sub(r"\s+", " ", t).strip()
    t = re.sub(r"^(please |pls )?(speak |reply |answer |talk |respond |change language to |language )?(in |to )?", "", t)
    t = re.sub(r"( language| please)$", "", t).strip()
    return _LANG_WORDS.get(t)
