<<<<<<< HEAD
# 🙏 Sudarshan AI — Free TTD WhatsApp Pilgrim Chatbot

A **100% free** WhatsApp AI chatbot that answers pilgrim questions about
Tirumala Tirupati Devasthanams (TTD) — darshan & tickets, accommodation,
transport, temple history, dress code, annadanam & laddus, and help/contact
info. It replies in **English and Telugu**, and needs **no database** —
everything it knows lives inside the code (`knowledge_base.py`).

This guide is written so that **even a complete beginner** can follow it
step by step. No coding experience required — just copy, paste, and click.

---

## 🧠 How it works (in plain English)

```
Pilgrim on WhatsApp
        │
        ▼
Meta WhatsApp Cloud API  (free, official WhatsApp messaging)
        │  sends the message to your webhook
        ▼
Your Flask server on Render (free hosting)
        │  looks up knowledge_base.py, and/or asks Groq AI to phrase the answer
        ▼
Groq AI (free, super-fast LLM API) — only used to write natural, bilingual
        replies USING your knowledge base — it cannot make things up outside it
        │
        ▼
Flask sends the reply back through WhatsApp Cloud API
        │
        ▼
Pilgrim gets an instant answer on WhatsApp 🙏
```

**The 3 free services you'll use:**
| Service | What it does | Cost |
|---|---|---|
| **Meta for Developers** (WhatsApp Cloud API) | Lets your bot send/receive WhatsApp messages | Free |
| **Groq** | Super-fast AI that writes the actual reply text | Free tier |
| **Render** | Hosts your Flask app 24/7 on the internet | Free tier |

**About "gunicorn" vs "uvicorn":** You mentioned uvicorn — that's normally
used for *async* frameworks like FastAPI. Since we're using **Flask**
(a classic, beginner-friendly framework), the standard production server is
**gunicorn**, which is already wired up for you in the `Procfile`. You don't
need to touch it — Render will use it automatically. Everything else is
exactly what you asked for: just **Flask + requests + gunicorn**, no database.

---

## 📁 What's in this folder

```
sudarshan-ai-ttd-chatbot/
├── app.py                # The Flask server (webhook + AI logic) — the brain
├── knowledge_base.py      # ALL pilgrim Q&A content — the "database" (in code!)
├── test_local.py          # Chat with your bot in the terminal (no WhatsApp needed)
├── requirements.txt       # The 3 Python packages needed (Flask, requests, gunicorn)
├── Procfile                # Tells Render how to start the app
├── render.yaml             # One-click Render deployment blueprint
├── .env.example             # Template for your secret keys
├── .gitignore                # Keeps your secrets out of GitHub
└── README.md                  # You are here
```

---

## ✅ STEP 1 — Get a free Groq API key (the "AI brain")

1. Go to **https://console.groq.com**
2. Sign up (free — email or Google login).
3. Click **API Keys** in the left menu → **Create API Key**.
4. Give it any name (e.g. `sudarshan-ai`) → copy the key that starts with `gsk_...`.
5. Save it somewhere safe — you'll paste it into Render later as `GROQ_API_KEY`.

That's it — Groq's free tier is generous enough for a pilgrim FAQ bot.

---

## ✅ STEP 2 — Put the code on GitHub

You need GitHub because Render deploys directly from a GitHub repository.

1. Go to **https://github.com** and sign up if you don't have an account.
2. Click the **+** icon (top right) → **New repository**.
3. Name it `sudarshan-ai-ttd-chatbot` → keep it **Public** or **Private**, your choice → **Create repository**.
4. On the new repo page, click **"uploading an existing file"**.
5. Drag and drop **all the files from this folder** (unzip it first) into the upload box.
6. Scroll down → **Commit changes**.

> 💡 If you know Git, you can instead run:
> ```bash
> git init
> git add .
> git commit -m "Sudarshan AI TTD chatbot"
> git branch -M main
> git remote add origin https://github.com/YOUR_USERNAME/sudarshan-ai-ttd-chatbot.git
> git push -u origin main
> ```

---

## ✅ STEP 3 — Deploy on Render (free hosting)

1. Go to **https://render.com** → sign up (you can use your GitHub account to sign in — easiest option).
2. Click **New +** → **Web Service**.
3. Connect your GitHub account if asked, then select your `sudarshan-ai-ttd-chatbot` repository.
4. Render will detect the `render.yaml` file automatically. If it asks you to
   confirm settings, use:
   - **Name:** `sudarshan-ai-ttd-chatbot`
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app --bind 0.0.0.0:$PORT`
   - **Plan:** **Free**
5. Under **Environment Variables**, add these (click "Add Environment Variable" for each):

   | Key | Value |
   |---|---|
   | `VERIFY_TOKEN` | Make up any word, e.g. `sudarshan123` |
   | `GROQ_API_KEY` | Paste the key from Step 1 |
   | `WHATSAPP_TOKEN` | *(leave blank for now — you'll add it in Step 5)* |
   | `PHONE_NUMBER_ID` | *(leave blank for now — you'll add it in Step 5)* |

6. Click **Create Web Service**. Render will build and deploy — takes 2-3 minutes.
7. When it's done, you'll get a public URL like:
   ```
   https://sudarshan-ai-ttd-chatbot.onrender.com
   ```
   Your webhook URL will be this **+ `/webhook`**, e.g.:
   ```
   https://sudarshan-ai-ttd-chatbot.onrender.com/webhook
   ```
   **Copy this — you'll need it in the next step.**

> ⚠️ Free Render web services "sleep" after 15 minutes of no traffic and take
> ~30–50 seconds to wake up on the next message. This is normal for free
> hosting. If you outgrow this, Render's paid tier removes the sleep delay.

---

## ✅ STEP 4 — Set up WhatsApp on Meta for Developers

1. Go to **https://developers.facebook.com** → log in with a Facebook account (or create one).
2. Click **My Apps** → **Create App**.
3. Choose the use case **"Other"** → **Business** → give your app a name (e.g. `Sudarshan AI`) → **Create App**.
4. On your new app's dashboard, find **WhatsApp** in the product list → click **Set up**.
5. This opens the **WhatsApp → API Setup** page. Here you'll see:
   - A **temporary access token** (valid 24 hours — good for testing).
   - A **test phone number** already provided by Meta for free.
   - A **Phone Number ID** (a long number — copy this).
6. Copy the **temporary access token** and the **Phone Number ID**.
7. Go back to **Render → your service → Environment** and paste them in:
   - `WHATSAPP_TOKEN` = the access token
   - `PHONE_NUMBER_ID` = the phone number ID
8. Click **Save Changes** — Render will redeploy automatically.

### Connect the webhook
1. Still on the WhatsApp **API Setup** page in Meta, find **Webhook** (or go to **WhatsApp → Configuration**).
2. Click **Edit** and enter:
   - **Callback URL:** `https://YOUR-RENDER-URL.onrender.com/webhook`
   - **Verify Token:** the same word you put in `VERIFY_TOKEN` on Render (e.g. `sudarshan123`)
3. Click **Verify and Save**. If it turns green ✅, your server is connected correctly.
4. Under **Webhook fields**, click **Manage** → subscribe to **`messages`**.

### Test it!
1. On the Meta API Setup page, there's a **"Send and receive messages"** section with a test number you can add on WhatsApp (usually add it to your phone contacts, or use the "Add recipient number" field for your own number).
2. Open WhatsApp on your phone, message that test number: **"Hi"**.
3. You should get the menu reply from Sudarshan AI within a few seconds! 🎉

> 📌 **Note on the free/temporary token:** Meta's default access token expires
> in 24 hours. For a permanent free setup:
> - Go to **Meta Business Suite → System Users**, create a system user, assign
>   it to your WhatsApp app with `whatsapp_business_messaging` permission, and
>   generate a **permanent token**. Use that instead of the temporary one.
> - This part is 100% free — Meta only charges per conversation once you
>   exceed the free monthly conversation limit, which is generous for a small
>   pilgrim FAQ bot.

---

## ✅ STEP 5 — Test locally before going live (optional but recommended)

You can chat with your bot in the terminal, without touching WhatsApp at all:

```bash
# 1. Install the packages
pip install -r requirements.txt

# 2. Set your Groq key for this terminal session
export GROQ_API_KEY=gsk_your_key_here      # Mac/Linux
set GROQ_API_KEY=gsk_your_key_here          # Windows

# 3. Chat!
python test_local.py
```

Type things like:
- `hi`
- `5` (to see the dress code menu)
- `Can I wear jeans?`
- `SSD టోకెన్లు ఎప్పుడు వస్తాయి?` (Telugu question — it should reply in Telugu)

---

## ➕ How to add or edit knowledge

Open `knowledge_base.py`. Find the category (e.g. `"darshan"`, `"rules"`, etc.)
and add a new entry to its `"qas"` list:

```python
{"q": "Your new question here?",
 "a": "Your new answer here."},
```

Save, push to GitHub, and Render will redeploy automatically (usually within a minute).
No database migrations, no restarts to configure — it's just Python.

---

## 🛠️ Troubleshooting

| Problem | Fix |
|---|---|
| Webhook verification fails on Meta | Make sure `VERIFY_TOKEN` on Render **exactly matches** what you typed into Meta (case-sensitive). |
| Bot doesn't reply at all | Check Render → **Logs** tab for errors. Also confirm you clicked **Subscribe** to `messages` in the Meta webhook fields. |
| Bot replies "AI brain is not configured" | Your `GROQ_API_KEY` is missing/wrong on Render → Environment tab. |
| First message after a while is slow | Normal — free Render services sleep after inactivity and take ~30-50s to wake up. |
| WhatsApp token stopped working after a day | You're using the temporary 24-hour token — set up a permanent System User token (see Step 4 note). |

---

## 🎉 That's it!

You now have a completely free, bilingual, database-free WhatsApp AI
assistant for TTD pilgrims — built with nothing more than Flask, requests,
and gunicorn, running on Render, powered by Groq, and connected through
Meta's official WhatsApp Cloud API.

🙏 Om Namo Venkatesaya!
=======
# sudarshan-ai
>>>>>>> 0fdba61651f6a6c413a72af67aad52126b6bb65f
