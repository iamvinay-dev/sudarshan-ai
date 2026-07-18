# -*- coding: utf-8 -*-
"""
test_local.py
--------------
A tiny command-line chat so you can test Sudarshan AI's brain
WITHOUT setting up WhatsApp or Meta at all.

Run it with:
    python test_local.py

Make sure you've set your GROQ_API_KEY first (see README.md, Step 3),
either in a .env file (loaded automatically if python-dotenv is installed)
or by exporting it in your terminal:
    export GROQ_API_KEY=your_key_here      (Mac/Linux)
    set GROQ_API_KEY=your_key_here         (Windows cmd)
"""

import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv is optional; env vars can also be set manually

from app import handle_incoming_text  # noqa: E402  (import after env load)

print("🙏 Sudarshan AI - Local Test Chat")
print("Type your message (English or Telugu). Type 'exit' to quit.\n")

FAKE_USER = "local_tester"

while True:
    user_input = input("You: ").strip()
    if user_input.lower() in {"exit", "quit"}:
        print("Bye! 🙏")
        break
    if not user_input:
        continue
    reply = handle_incoming_text(FAKE_USER, user_input)
    print(f"\nSudarshan AI:\n{reply}\n")
