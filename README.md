# 🙏 Sudarshan AI — TTD Pilgrim WhatsApp Assistant

Sudarshan AI is a WhatsApp chatbot that helps pilgrims visiting Tirumala (TTD). It answers questions about darshan and tickets, accommodation, transport, temple history, dress code, annadanam, laddu and contact details, and it lets pilgrims register complaints and bribe reports. TTD staff manage everything from a private admin website.

It is built with **Python + Flask**, uses **Supabase** for storage, and **Groq / Cohere / Gemini** only to phrase answers from verified facts.

---

## ✨ Features

**For pilgrims (on WhatsApp)**
- Number menu (1–7) plus free-text questions, in **English and Telugu** (including Telugu typed in English letters).
- Hindi, Kannada, Tamil, Malayalam, Bengali, Gujarati, Odia, Punjabi and Urdu are understood by translating to English and back. A pilgrim can also switch language by typing a language name, e.g. "Kannada".
- **Live notices** typed by TTD staff (SSD token timings, ticket availability, crowd status, one-day rules). If staff posted nothing, the bot says so honestly and points to tirumala.org instead of guessing.
- **Complaints and bribe reports** with a reference number (e.g. `C-1042`) and an optional anonymous mode.
- **Feedback**: "Was your question solved?" with a 1–5 rating.
- Conversation memory (last 5 exchanges) that survives restarts and multiple workers.

**For TTD staff (admin website at `/admin`)**
- Secure login: hashed passwords, lockout, rate limit, CSRF protection, 30-minute idle timeout, audit log.
- Live dashboard (refreshes every 5 seconds), question list with filters and CSV export.
- Notices page, complaints page with a 24-hour deadline, bribe reports, feedback page.
- Roles: `officer` (default), `senior`, `vigilance`, `super`.

**Safety and privacy**
- Prompt-injection, off-topic and "what model are you" questions are blocked by `guardrails.py` (no AI call, no cost). AI replies are cleaned so they never leak model, provider or prompt details.
- Phone numbers are never stored in plain text. Pilgrims appear as anonymous codes like `#1001`.
- Questions are redacted (phone numbers, emails, ID-like strings) before saving.
- A pilgrim's number is saved **encrypted** only when they report a problem and did not choose anonymous. Admin pages never read it.
- Complaint text is never sent to an AI model.

---

## 🧠 How a message is answered

Every message goes through this order, and the first match wins:

1. Active complaint or feedback conversation
2. Menu number or greeting
3. Complaint intent ("complaint", "bribe", "లంచం" …)
4. Guardrails (injection, bot questions, small talk, off-topic) and vague messages
5. Live notices from TTD staff
6. Direct knowledge-base match (with an intent check)
7. Answer cache
8. AI (Groq, then Cohere, then Gemini as fallbacks), **only if the facts clearly answer the question**. Otherwise the bot says it doesn't have the answer, logs it as unanswered, and offers to register a complaint.

---

## 📁 Project structure

| File | What it does |
|---|---|
| `app.py` | Flask app: WhatsApp webhook, reply pipeline, AI calls, translation |
| `knowledge_base.py` | Pilgrim Q&A content and menus (English + Telugu). Fallback if Supabase is down |
| `guardrails.py` | Input screening and AI-reply sanitising |
| `languages.py` | Language detection and language switching |
| `complaints.py` | Complaint, bribe-report and feedback conversations |
| `notices.py` | Live notices shown to pilgrims |
| `session_store.py` | Per-pilgrim conversation memory in Supabase |
| `db.py` | Supabase layer: privacy hashing, logging, cache, KB loading, encryption |
| `admin.py` | Admin website: login, dashboard, questions, pilgrims, CSV export |
| `admin_extra.py` | Admin pages for notices, complaints, bribe reports, feedback |
| `test_local.py` | Chat with the bot in your terminal, no WhatsApp needed |
| `Procfile`, `render.yaml` | Start command and Render deployment settings |

---

## 🧰 Services used

| Service | Purpose |
|---|---|
| Meta WhatsApp Cloud API | Receives and sends WhatsApp messages |
| Supabase | Database (logs, cache, notices, complaints, admin users, conversations) |
| Groq | Main AI model for phrasing and translation |
| Cohere, Gemini | Optional AI fallbacks |
| Render | Hosting (free plan works; it sleeps when idle) |

Free tiers and limits change, so check each provider's current terms.

---

## 🔐 Environment variables

Set these in Render → Environment (or in a local `.env` file, which is git-ignored).

| Variable | Required | Notes |
|---|---|---|
| `VERIFY_TOKEN` | Yes | Your own word; must match the one entered in Meta (case-sensitive) |
| `WHATSAPP_TOKEN` | Yes | WhatsApp Cloud API access token |
| `PHONE_NUMBER_ID` | Yes | From Meta → WhatsApp → API Setup |
| `GROQ_API_KEY` | Yes | From the Groq Console (starts with `gsk_`) |
| `SUPABASE_URL` | Yes | e.g. `https://abcdxyz.supabase.co` |
| `SUPABASE_SERVICE_KEY` | Yes | Supabase **secret** key. Server only, never share |
| `PHONE_HASH_SECRET` | Yes | Long random text. Set once and **never change it** |
| `PHONE_ENC_SECRET` | For contact-back | 40+ random characters. Set once and **never change it** |
| `SECRET_KEY` | For admin | Long random text, 32+ characters. Admin site stays off without it |
| `ADMIN_BOOTSTRAP_USER` | First run | First admin username (used only when no admin exists) |
| `ADMIN_BOOTSTRAP_PASSWORD` | First run | First admin password (must be changed at first login) |
| `META_APP_SECRET` | Optional | Enables verification of Meta's webhook signature (recommended) |
| `COHERE_API_KEY`, `GEMINI_API_KEY` | Optional | AI fallbacks |
| `GROQ_MODEL`, `COHERE_MODEL`, `GEMINI_MODEL` | Optional | Override default models |
| `WHATSAPP_API_VERSION` | Optional | Default `v20.0` |
| `CACHE_TTL_HOURS` | Optional | Default `8`. Cached answers are deleted after this long |
| `CONV_RETENTION_HOURS` | Optional | Default `8`. Saved chats are deleted after this long |
| `CRON_TOKEN` | Optional | Lets a free cron job call `/internal/escalate` |
| `MIGRATE_TOKEN` | Temporary | Only for the one-time knowledge-base copy to Supabase. Remove afterwards |
| `ADMIN_ALLOW_HTTP` | Local only | Allows admin login over plain HTTP for local testing |

⚠️ Never commit keys or tokens to GitHub.

---

## 🚀 Deploy

1. **Supabase**: create a project and the tables the code uses: `pilgrims`, `queries`, `answer_cache`, `kb_categories`, `kb_qas`, `feedback`, `conversations`, `notices`, `complaints`, `complaint_events`, `admin_users`, `admin_audit`. *(The SQL schema is not in this repo yet. Add it as `schema.sql` so setup is repeatable.)*
2. **Render**: New + → Web Service → select this repo. It reads `render.yaml`.
   - Build command: `pip install -r requirements.txt`
   - Start command: `gunicorn app:app --bind 0.0.0.0:$PORT`
3. Add the environment variables above in Render.
4. **Meta**: in WhatsApp → Configuration, set the callback URL to `https://YOUR-SERVICE.onrender.com/webhook` and the verify token to your `VERIFY_TOKEN`. Subscribe to the **messages** field.
5. **One-time knowledge-base copy**: set `MIGRATE_TOKEN`, open `/internal/migrate-kb?token=YOUR_TOKEN` once, then remove the variable.
6. Open `/admin` and log in with the bootstrap admin, then change the password.
7. Send "Hi" to your WhatsApp number to test.

**About tokens:** Meta's temporary access token expires in 24 hours. For a long-running bot, create a System User in Meta Business Suite with `whatsapp_business_messaging` permission and generate a permanent token.

**Render free plan:** the service sleeps when idle, so the first reply after a quiet period can take 30–50 seconds.

---

## 🌐 Routes

| Route | Purpose |
|---|---|
| `GET /` | Health check |
| `GET/POST /webhook` | WhatsApp verification and incoming messages |
| `GET /internal/migrate-kb` | One-time knowledge-base migration (needs `MIGRATE_TOKEN`) |
| `GET /internal/escalate` | Escalates complaints older than 24 hours (needs `CRON_TOKEN`) |
| `/admin/*` | Admin website |

---

## 🧪 Test locally

```bash
pip install -r requirements.txt
export GROQ_API_KEY=gsk_your_key_here     # Windows: set GROQ_API_KEY=gsk_your_key_here
python test_local.py
```

Try: `hi`, `5`, `Can I wear jeans?`, or a Telugu question. Without Supabase variables the bot still works using the Python knowledge base and RAM memory.

---

## ✏️ Update the knowledge base

- **Daily changes** (token timings, ticket availability): use the **Notices** page in the admin site. It reaches the bot within about 30 seconds.
- **Permanent content**: edit `knowledge_base.py`, add `{"q": "...", "a": "..."}` to a category's `qas` list, and push to GitHub. Render redeploys automatically. The bot reloads the knowledge base from Supabase every 5 minutes, so re-run the migration if Supabase holds the live copy.

---

## 🛠️ Troubleshooting

| Problem | Check |
|---|---|
| Meta webhook verification fails | `VERIFY_TOKEN` in Render must match Meta exactly |
| Bot doesn't reply | Render Logs tab; confirm the `messages` field is subscribed; check `WHATSAPP_TOKEN` hasn't expired |
| Bot says the AI is not configured | `GROQ_API_KEY` missing or wrong in Render |
| `/admin` shows nothing or login fails | `SECRET_KEY` and the bootstrap admin variables must be set |
| Pilgrim IDs reset or logging is off | `PHONE_HASH_SECRET` or Supabase variables missing |
| "Send WhatsApp message" to a pilgrim fails | WhatsApp allows it only within 24 hours of the pilgrim's last message |
| First reply is very slow | Render free plan was asleep |

---

🙏 *Om Namo Venkatesaya!*
