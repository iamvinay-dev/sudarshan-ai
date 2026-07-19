# -*- coding: utf-8 -*-
"""
app.py
------
Sudarshan AI - a free WhatsApp chatbot for TTD (Tirumala Tirupati Devasthanams)
pilgrims, built with:
    - Flask            (web server / webhook receiver)
    - requests          (to call the Groq AI API and the WhatsApp Cloud API)
    - gunicorn           (production server used by Render, see Procfile)

NO DATABASE is used. All knowledge lives in knowledge_base.py.
Only a tiny in-memory dict is used to remember the last few chat turns
per user (this resets whenever the server restarts, which is fine for a
free pilgrim FAQ bot).

Flow:
    1. Meta sends a GET request to /webhook to verify your server (once).
    2. Every time a pilgrim sends a WhatsApp message, Meta POSTs it to /webhook.
    3. We read the message, decide the reply (menu / category / AI answer),
       and send it back using the WhatsApp Cloud API.
"""

import os
import time
import logging
import requests
from flask import Flask, request, jsonify

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover
    load_dotenv = None

try:
    import json
except ImportError:  # pragma: no cover
    json = None

if load_dotenv is not None:
    load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

from knowledge_base import (
    CATEGORY_MAP,
    WELCOME_MESSAGE,
    TELUGU_WELCOME_MESSAGE,
    build_category_reply,
    get_relevant_knowledge_text,
    find_best_direct_match,
    format_direct_answer,
)

# ---------------------------------------------------------------------------
# Configuration (all read from Environment Variables — see .env.example)
#
# Two AI providers are configured, both with generous FREE tiers:
#   1) GEMINI  (primary)  — Google's Gemini API, tried first.
#   2) GROQ    (backup)   — used automatically if Gemini is not configured,
#                           fails, or is rate-limited.
# Keeping two independent providers means a rate limit or outage on one
# doesn't take the whole bot down — and between the DIRECT-MATCH engine in
# knowledge_base.py and this two-provider fallback, actual paid-API calls
# are kept to a minimum.
# ---------------------------------------------------------------------------
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "sudarshan_verify_token")
WHATSAPP_TOKEN = os.environ.get("WHATSAPP_TOKEN", "")
PHONE_NUMBER_ID = os.environ.get("PHONE_NUMBER_ID", "")
WHATSAPP_API_VERSION = os.environ.get("WHATSAPP_API_VERSION", "v20.0")

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash")

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
GROQ_MODEL = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("sudarshan-ai")

app = Flask(__name__)

# Tiny in-memory "session" store: { phone_number: [ {role, content}, ... ] }
# This is NOT a database — it just lives in RAM and resets on restart.
user_sessions = {}
MAX_HISTORY_TURNS = 3  # keep last 3 user+bot exchanges per person

# Remembers each pilgrim's last-used language ("en" or "te") so that a bare
# menu number (e.g. "1") replies in the right language even though a digit
# by itself carries no language information.
user_lang = {}

# ---------------------------------------------------------------------------
# System prompt TEMPLATE (the {knowledge} part is filled in per-question,
# with ONLY the handful of Q&As relevant to that question — see ask_groq()
# below). Previously the ENTIRE knowledge base (~24,000 characters, 6,000+
# tokens) was embedded here and sent on every single message, which used up
# Groq's free-tier tokens-per-minute budget almost instantly and caused
# "429 Too Many Requests" errors on the very next question.
# ---------------------------------------------------------------------------
SYSTEM_PROMPT_TEMPLATE = """You are "Sudarshan AI", a warm, respectful WhatsApp assistant that helps
pilgrims visiting Tirumala Tirupati Devasthanams (TTD) temple, Andhra Pradesh, India.

RULES YOU MUST FOLLOW:
1. Answer ONLY using the KNOWLEDGE BASE provided below. Do not invent facts,
   phone numbers, prices, or dates that are not present in it.
2. If the answer is not in the knowledge base, politely say you don't have that
   exact detail and point the pilgrim to the official TTD website https://tirumala.org
   or the TTD Call Centre. Never make up information.
3. LANGUAGE: Reply in the SAME language the pilgrim used.
   - If they write in Telugu (Telugu script or Romanized "Tenglish"), reply in Telugu.
   - If they write in English, reply in English.
   - Keep the tone respectful and simple — many pilgrims are elderly or first-time users.
4. Keep answers short and WhatsApp-friendly: use short paragraphs, simple words,
   and emojis sparingly (🙏 🛕 🎟️ 🚌 🏨) where natural.
5. Be warm and devotional in tone, like a helpful temple volunteer, but stay factual.
6. If asked something totally unrelated to Tirumala/TTD pilgrimage, gently redirect
   the conversation back to how you can help with their Tirumala visit.

KNOWLEDGE BASE (the only source of truth you may use for THIS question):
{knowledge}
"""

# ---------------------------------------------------------------------------
# PROVIDER 1: Gemini AI call (PRIMARY — tried first)
# ---------------------------------------------------------------------------
def ask_gemini(user_message: str, history: list, system_prompt: str):
    """Call Google's Gemini API (free tier). Returns the reply text on
    success, or None on any failure — so the caller can fall back to Groq
    without the pilgrim ever seeing an error."""
    if not GEMINI_API_KEY:
        return None

    # Gemini's REST API uses "contents" with role "user"/"model" (not
    # "assistant"), and takes the system prompt as a separate field.
    contents = []
    for turn in history:
        role = "model" if turn["role"] == "assistant" else "user"
        contents.append({"role": role, "parts": [{"text": turn["content"]}]})
    contents.append({"role": "user", "parts": [{"text": user_message}]})

    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
    )
    payload = {
        "system_instruction": {"parts": [{"text": system_prompt}]},
        "contents": contents,
        "generationConfig": {"temperature": 0.3, "maxOutputTokens": 400},
    }

    try:
        response = requests.post(url, json=payload, timeout=20)

        if response.status_code == 429:
            log.warning("Gemini rate-limited (429) — falling back to Groq.")
            return None

        response.raise_for_status()
        data = response.json()
        candidates = data.get("candidates") or []
        if not candidates:
            log.warning("Gemini returned no candidates — falling back to Groq.")
            return None
        parts = candidates[0].get("content", {}).get("parts", [])
        text = "".join(p.get("text", "") for p in parts).strip()
        return text or None

    except Exception as exc:  # noqa: BLE001 - never crash the bot, just fall back
        log.error("Gemini API error: %s — falling back to Groq.", exc)
        return None


# ---------------------------------------------------------------------------
# PROVIDER 2: Groq AI call (BACKUP — used only if Gemini is unavailable)
# ---------------------------------------------------------------------------
def ask_groq(user_message: str, history: list, system_prompt: str):
    """Send the conversation to Groq's OpenAI-compatible chat completion API.
    Returns the reply text on success, or None on failure (so the caller
    can show a single graceful final message instead of a raw error)."""
    if not GROQ_API_KEY:
        return None

    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(history)
    messages.append({"role": "user", "content": user_message})

    payload = {
        "model": GROQ_MODEL,
        "messages": messages,
        "temperature": 0.3,
        "max_tokens": 400,
    }
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    # Try once, and if we hit Groq's rate limit (429), wait briefly and
    # retry ONE more time before giving up.
    for attempt in range(2):
        try:
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=20,
            )

            if response.status_code == 429:
                retry_after = response.headers.get("Retry-After")
                wait_seconds = min(float(retry_after) if retry_after else 2.0, 5.0)
                log.warning(
                    "Groq rate limit hit (429) on attempt %d. Retrying in %.1fs...",
                    attempt + 1, wait_seconds,
                )
                if attempt == 0:
                    time.sleep(wait_seconds)
                    continue
                return None

            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"].strip()

        except Exception as exc:  # noqa: BLE001 - keep the bot alive no matter what
            log.error("Groq API error: %s", exc)
            return None

    return None


# ---------------------------------------------------------------------------
# ORCHESTRATOR: try Gemini first, then Groq, then a graceful final message.
# This is only reached when the DIRECT-MATCH engine in knowledge_base.py
# (zero API cost) couldn't confidently answer the question by itself.
# ---------------------------------------------------------------------------
def get_ai_reply(user_message: str, history: list) -> str:
    # Only pull in the Q&As relevant to THIS question (usually 6 of them,
    # a few hundred tokens) instead of the whole knowledge base — this is
    # what fixed the earlier Groq 429 "Too Many Requests" errors, and it
    # keeps Gemini's free-tier usage low too.
    relevant_knowledge = get_relevant_knowledge_text(user_message, top_n=6)
    system_prompt = SYSTEM_PROMPT_TEMPLATE.format(knowledge=relevant_knowledge)

    # 1) PRIMARY: Gemini (free tier)
    reply = ask_gemini(user_message, history, system_prompt)
    if reply:
        return reply

    # 2) BACKUP: Groq (free tier) — only reached if Gemini is not
    #    configured, failed, or was rate-limited.
    reply = ask_groq(user_message, history, system_prompt)
    if reply:
        return reply

    # 3) Both providers unavailable — never show a raw error to a pilgrim.
    if not GEMINI_API_KEY and not GROQ_API_KEY:
        return ("⚠️ The AI brain is not configured yet (missing GEMINI_API_KEY "
                "and GROQ_API_KEY). Please try one of the menu numbers 1-7, "
                "or contact the admin.")
    return ("🙏 Sorry, I'm having trouble thinking right now. "
            "Please try again in a moment, or reply with a menu number (1-7).")


# ---------------------------------------------------------------------------
# WhatsApp Cloud API helpers
# ---------------------------------------------------------------------------
def send_whatsapp_message(to: str, text: str) -> None:
    """Send a plain text WhatsApp message via Meta's Cloud API."""
    if not WHATSAPP_TOKEN or not PHONE_NUMBER_ID:
        log.warning("WHATSAPP_TOKEN / PHONE_NUMBER_ID not set — skipping send. "
                     "Reply would have been:\n%s", text)
        return

    url = f"https://graph.facebook.com/{WHATSAPP_API_VERSION}/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json",
    }
    # WhatsApp caps a single text message around 4096 chars; trim to be safe.
    safe_text = text[:4000]
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": safe_text},
    }
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=15)
        if resp.status_code >= 400:
            log.error("WhatsApp send failed [%s]: %s", resp.status_code, resp.text)
    except Exception as exc:  # noqa: BLE001
        log.error("WhatsApp send exception: %s", exc)


# ---------------------------------------------------------------------------
# Core message-handling logic
# ---------------------------------------------------------------------------
GREETING_WORDS = {
    "hi", "hello", "hey", "start", "menu", "namaste", "hai", "hlo",
    "నమస్తే", "నమస్కారం", "హాయ్", "మెనూ", "start menu",
}


def is_telugu(text: str) -> bool:
    """Very simple check: does the text contain Telugu unicode characters?"""
    return any("\u0c00" <= ch <= "\u0c7f" for ch in text)


def handle_incoming_text(from_number: str, text: str) -> str:
    clean = text.strip()
    lowered = clean.lower()

    # Remember the pilgrim's language whenever we can actually detect one
    # from real words (a bare digit like "1" tells us nothing about language,
    # so we don't touch the stored preference in that case).
    if is_telugu(clean):
        user_lang[from_number] = "te"
    elif not clean.isdigit() and lowered not in GREETING_WORDS:
        user_lang[from_number] = "en"

    telugu_pref = user_lang.get(from_number) == "te"

    # 1) Numbered menu selection (1-7) → SHORT bullet-point summary only.
    #    Full Q&A detail is given later, only if the pilgrim asks a question.
    if clean in CATEGORY_MAP:
        return build_category_reply(CATEGORY_MAP[clean], telugu=telugu_pref)

    # 2) Greeting / menu request
    if lowered in GREETING_WORDS or clean in {"0", "9"}:
        if is_telugu(clean):
            user_lang[from_number] = "te"
            return TELUGU_WELCOME_MESSAGE
        return WELCOME_MESSAGE

    # 3) DIRECT MATCH (zero API cost): if the expanded keyword/synonym
    #    engine in knowledge_base.py is confident it found the right Q&A,
    #    answer straight from the knowledge base — no Gemini/Groq call at
    #    all. This is what keeps day-to-day running cost near zero.
    direct = find_best_direct_match(clean)
    if direct:
        reply = format_direct_answer(direct, telugu=telugu_pref)
        history = user_sessions.get(from_number, [])
        history.append({"role": "user", "content": clean})
        history.append({"role": "assistant", "content": reply})
        user_sessions[from_number] = history[-(MAX_HISTORY_TURNS * 2):]
        return reply

    # 4) No confident direct match — ask the AI (Gemini first, Groq as
    #    backup), grounded with only the few Q&As relevant to this question.
    #    This is the ONLY path that calls a paid/rate-limited API.
    history = user_sessions.get(from_number, [])
    reply = get_ai_reply(clean, history)

    history.append({"role": "user", "content": clean})
    history.append({"role": "assistant", "content": reply})
    user_sessions[from_number] = history[-(MAX_HISTORY_TURNS * 2):]

    return reply


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "ok",
        "service": "Sudarshan AI - TTD WhatsApp Chatbot",
        "message": "Server is running. Configure this URL + /webhook in Meta Developer Console."
    })


@app.route("/webhook", methods=["GET"])
def verify_webhook():
    """Meta calls this once to verify ownership of the webhook URL."""
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        log.info("Webhook verified successfully.")
        return challenge, 200
    log.warning("Webhook verification failed.")
    return "Verification failed", 403


@app.route("/webhook", methods=["POST"])
def receive_webhook():
    """Meta POSTs every incoming WhatsApp event here."""
    data = request.get_json(silent=True) or {}
    log.info("Incoming webhook payload: %s", data)

    try:
        entry = data.get("entry", [])[0]
        changes = entry.get("changes", [])[0]
        value = changes.get("value", {})
        messages = value.get("messages")

        if not messages:
            log.info("Webhook event had no messages; likely a status update.")
            return "OK", 200

        message = messages[0]
        from_number = message.get("from", "unknown")
        msg_type = message.get("type")
        log.info("Processing message from %s with type %s", from_number, msg_type)

        if msg_type == "text":
            text_body = message.get("text", {}).get("body", "")
            reply_text = handle_incoming_text(from_number, text_body)
        elif msg_type == "interactive":
            interactive = message.get("interactive", {})
            selection = (
                interactive.get("button_reply", {}).get("title")
                or interactive.get("list_reply", {}).get("title")
                or ""
            )
            reply_text = handle_incoming_text(from_number, selection)
        else:
            reply_text = WELCOME_MESSAGE

        send_whatsapp_message(from_number, reply_text)

    except (IndexError, KeyError) as exc:
        log.info("No message payload to process (%s).", exc)

    return "OK", 200


# ---------------------------------------------------------------------------
# Local dev entrypoint (Render uses gunicorn via the Procfile instead)
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
