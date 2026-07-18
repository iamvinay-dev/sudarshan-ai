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
import logging
import requests
from flask import Flask, request, jsonify

from knowledge_base import (
    CATEGORY_MAP,
    WELCOME_MESSAGE,
    TELUGU_WELCOME_MESSAGE,
    build_category_reply,
    get_full_knowledge_text,
)

# ---------------------------------------------------------------------------
# Configuration (all read from Environment Variables — see .env.example)
# ---------------------------------------------------------------------------
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "sudarshan_verify_token")
WHATSAPP_TOKEN = os.environ.get("WHATSAPP_TOKEN", "")
PHONE_NUMBER_ID = os.environ.get("PHONE_NUMBER_ID", "")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
GROQ_MODEL = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")
WHATSAPP_API_VERSION = os.environ.get("WHATSAPP_API_VERSION", "v20.0")

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("sudarshan-ai")

app = Flask(__name__)

# Tiny in-memory "session" store: { phone_number: [ {role, content}, ... ] }
# This is NOT a database — it just lives in RAM and resets on restart.
user_sessions = {}
MAX_HISTORY_TURNS = 3  # keep last 3 user+bot exchanges per person

# ---------------------------------------------------------------------------
# Build the system prompt ONCE at startup (knowledge base is small enough
# to fit fully into the prompt — this is called "prompt-based RAG").
# ---------------------------------------------------------------------------
KNOWLEDGE_TEXT = get_full_knowledge_text()

SYSTEM_PROMPT = f"""You are "Sudarshan AI", a warm, respectful WhatsApp assistant that helps
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

KNOWLEDGE BASE (the only source of truth you may use):
{KNOWLEDGE_TEXT}
"""

# ---------------------------------------------------------------------------
# Groq AI call
# ---------------------------------------------------------------------------
def ask_groq(user_message: str, history: list) -> str:
    """Send the conversation to Groq's OpenAI-compatible chat completion API
    and return the assistant's reply text."""
    if not GROQ_API_KEY:
        return ("⚠️ The AI brain is not configured yet (missing GROQ_API_KEY). "
                "Please try one of the menu numbers 1-7, or contact the admin.")

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(history)
    messages.append({"role": "user", "content": user_message})

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": GROQ_MODEL,
                "messages": messages,
                "temperature": 0.3,
                "max_tokens": 500,
            },
            timeout=20,
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"].strip()
    except Exception as exc:  # noqa: BLE001 - keep the bot alive no matter what
        log.error("Groq API error: %s", exc)
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

    # 1) Numbered menu selection (1-7)
    if clean in CATEGORY_MAP:
        return build_category_reply(CATEGORY_MAP[clean])

    # 2) Greeting / menu request
    if lowered in GREETING_WORDS or clean in {"0", "9"}:
        return TELUGU_WELCOME_MESSAGE if is_telugu(clean) else WELCOME_MESSAGE

    # 3) Otherwise, let the AI (Groq) answer using the knowledge base,
    #    with a little memory of the recent conversation.
    history = user_sessions.get(from_number, [])
    reply = ask_groq(clean, history)

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
    log.info("Incoming webhook: %s", data)

    try:
        entry = data.get("entry", [])[0]
        changes = entry.get("changes", [])[0]
        value = changes.get("value", {})
        messages = value.get("messages")

        if not messages:
            # Could be a status update (delivered/read) — nothing to do.
            return "OK", 200

        message = messages[0]
        from_number = message["from"]
        msg_type = message.get("type")

        if msg_type == "text":
            text_body = message["text"]["body"]
            reply_text = handle_incoming_text(from_number, text_body)
        elif msg_type == "interactive":
            # Handles button/list replies if you add interactive menus later.
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
