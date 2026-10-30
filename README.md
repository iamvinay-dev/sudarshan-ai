

Pasted markdown(20261030-133514).md
File
rewrite this whole thing md file in human formate

I've rewritten the complete Sudarshan AI documentation in a more natural, professional, human-friendly format.

What's improved
Removed Git merge conflict markers.

Improved grammar and sentence structure.

Made technical explanations easier for beginners.

Organized deployment instructions into clear steps.

Improved tables, headings, and code formatting.

Preserved the original project architecture and technical details.

Added clearer troubleshooting instructions.

Kept all important commands and configuration variables.

Download your updated Markdown file
📄 

You can directly use this as your project's README.md on GitHub. 



Library
/
Sudarshan_AI_Humanized_README.md



Sudarshan AI -- TTD WhatsApp Pilgrim Chatbot
Sudarshan AI is a WhatsApp chatbot designed to help pilgrims find
information about Tirumala Tirupati Devasthanams (TTD). It can
answer common questions about darshan and tickets, accommodation,
transport, temple history, dress code, annadanam, laddus, and useful
contact information.

The chatbot supports English and Telugu. It uses a Python knowledge
base instead of a separate database, so the information is maintained
directly in knowledge_base.py.

This guide explains how to set up and deploy the chatbot, step by step.
It is written for beginners, so you can follow along even if you have
limited coding experience.

1. How Sudarshan AI works
The chatbot follows a simple process:

A pilgrim sends a message to the Sudarshan AI WhatsApp number.

Meta's official WhatsApp Cloud API receives the message and forwards
it to the chatbot's webhook.

The Flask application hosted on Render receives the message.

The application checks the information stored in knowledge_base.py
and can use Groq AI to phrase the response naturally.

The reply is sent back to the pilgrim through the WhatsApp Cloud
API.

Groq is used to help write clear, natural replies in English or Telugu
using the chatbot's knowledge base. It is not intended to provide
information beyond that knowledge base.

Services used
Service Purpose Cost information

Meta for Developers -- Receives and sends Free access is
WhatsApp Cloud API WhatsApp messages available, subject to
Meta's current terms
and limits

Groq Generates Free tier available
natural-language
replies

Why this project uses Gunicorn instead of Uvicorn
This project is built with Flask, a beginner-friendly Python web
framework. Gunicorn is a standard production server for Flask
applications.

Uvicorn is more commonly used with asynchronous frameworks such as
FastAPI. The project's Procfile already contains the Gunicorn start
command, so you do not need to configure it separately.

The application uses Flask, requests, and Gunicorn. It does not
require a separate database.

2. Project folder structure
Your project folder should contain the following files:

sudarshan-ai-ttd-chatbot/
│
├── app.py                 # Flask application, webhook and AI logic
├── knowledge_base.py      # Questions and answers for TTD pilgrims
├── test_local.py          # Test the chatbot locally without WhatsApp
├── requirements.txt       # Required Python packages
├── Procfile               # Command used to start the application
├── render.yaml            # Render deployment configuration
├── .env.example           # Example template for secret environment variables
├── .gitignore             # Prevents secret files from being uploaded
└── README.md              # Project documentation
The main files to understand are:

app.py -- Runs the Flask server, receives WhatsApp messages,
and handles the chatbot logic.

knowledge_base.py -- Stores the questions and answers used by
Sudarshan AI.

test_local.py -- Lets you test the chatbot from your computer
before connecting WhatsApp.

requirements.txt -- Lists the Python packages needed to run
the project.

3. Create a Groq API key
Groq provides the AI service used to help Sudarshan AI write responses.

Open the Groq Console.

Create an account using your email address or Google account.

Open API Keys from the menu.

Select Create API Key.

Enter a name, such as sudarshan-ai.

Create the key and copy it. It usually begins with gsk_.

Store the key somewhere safe. You will add it to Render later.

When you configure Render, this key will be saved as the GROQ_API_KEY
environment variable.

Important: Do not publish your API key or upload it to GitHub.

4. Upload the project to GitHub
Render can deploy the application directly from a GitHub repository.
First, upload your project files to GitHub.

Open GitHub and sign in. Create an account if
you do not already have one.

Select the + icon in the top-right corner.

Choose New repository.

Enter this repository name:

sudarshan-ai-ttd-chatbot

Choose whether the repository should be public or private.

Select Create repository.

On the new repository page, choose uploading an existing file.

Extract the project ZIP file, then upload all the files inside the
project folder.

Scroll down and select Commit changes.

Alternative: Upload using Git
If Git is already installed on your computer, you can upload the project
through the terminal:

git init
git add .
git commit -m "Add Sudarshan AI TTD chatbot"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/sudarshan-ai-ttd-chatbot.git
git push -u origin main
Replace YOUR_USERNAME with your GitHub username.

5. Deploy the application on Render
Render will host your Flask application and provide a public URL for the
WhatsApp webhook.

Open Render and create an account.

You can sign in using your GitHub account.

From the dashboard, select New + and then Web Service.

Connect your GitHub account if Render asks you to.

Select the sudarshan-ai-ttd-chatbot repository.

Render should detect the project's render.yaml configuration file.

If you need to enter the settings manually, use the following values:

Setting Value

Name sudarshan-ai-ttd-chatbot
Runtime Python 3
Build Command pip install -r requirements.txt
Start Command gunicorn app:app --bind 0.0.0.0:$PORT
Plan Free

Add environment variables
In the service settings, find Environment Variables. Add the
following variables:

Variable Value

VERIFY_TOKEN Create your own verification word,
for example sudarshan123

GROQ_API_KEY Paste the Groq API key you created
in Step 3

WHATSAPP_TOKEN Leave blank for now. You will add
it in Step 6

Select Create Web Service.

Wait while Render installs the packages and deploys the application.
The initial deployment may take a few minutes.

Once deployment is complete, Render will provide a public service
URL similar to:

https://sudarshan-ai-ttd-chatbot.onrender.com
Your webhook URL is the same address followed by /webhook:

https://sudarshan-ai-ttd-chatbot.onrender.com/webhook
Copy this webhook URL. You will need it when configuring Meta.

Note about Render's free plan
Free Render web services may go to sleep after a period of inactivity.
When someone sends a message after the service has been idle, the first
response may take around 30--50 seconds while the service starts again.
This is a limitation of the free hosting plan.

6. Set up WhatsApp using Meta for Developers
Now connect the chatbot to the official WhatsApp Cloud API.

Open Meta for Developers.

Sign in using your Facebook account.

Open My Apps and select Create App.

Choose the Other use case, then select Business.

Enter an app name, such as Sudarshan AI, and create the app.

On the app dashboard, find WhatsApp in the product list.

Select Set up.

You should now be on the WhatsApp → API Setup page. Meta provides
the following details:

A temporary access token, which is suitable for testing and is valid
for 24 hours.

A test WhatsApp phone number.

A Phone Number ID.

Copy the temporary access token and the Phone Number ID.

Add the WhatsApp details to Render
Return to your Render dashboard.

Open your sudarshan-ai-ttd-chatbot service.

Go to Environment.

Add or update these two variables:

Variable Value

WHATSAPP_TOKEN The temporary access token from Meta
PHONE_NUMBER_ID The Phone Number ID from Meta

Select Save Changes. Render should redeploy the application
using the updated environment variables.

Connect the WhatsApp webhook
The webhook allows Meta to forward incoming WhatsApp messages to your
Flask application.

Return to the WhatsApp API Setup page in Meta.

Find the Webhook section. Depending on the dashboard layout, it
may also appear under WhatsApp → Configuration.

Select Edit.

Enter the following details:

Field Value

Callback URL https://YOUR-RENDER-URL.onrender.com/webhook

Replace YOUR-RENDER-URL with your actual Render service address. Make
sure the verification token matches exactly, including uppercase and
lowercase letters.

Select Verify and Save.

Once verification succeeds, open Webhook fields.

Select Manage and subscribe to the messages field.

Your WhatsApp webhook should now be connected to the Flask application.

Send a test message
On Meta's WhatsApp API Setup page, find the Send and receive
messages section.

Follow the instructions to add your own WhatsApp number as a test
recipient.

Open WhatsApp on your phone.

Send a message such as Hi to the test number provided by Meta.

If everything is configured correctly, Sudarshan AI should send a
reply.

Important: Temporary and permanent access tokens
The temporary access token provided by Meta expires after 24 hours. It
is useful for initial testing, but it is not suitable for a long-running
deployment.

For a longer-term setup, the original guide recommends creating a system
user in Meta Business Suite → System Users, assigning the required
WhatsApp app permissions (including whatsapp_business_messaging), and
generating a longer-lived access token. Use the token according to
Meta's current instructions and security requirements.

Meta's pricing and free usage limits can change, so check the current
WhatsApp Business Platform pricing and terms before relying on a
particular allowance.

7. Test the chatbot locally (optional)
You can test Sudarshan AI from your computer before connecting it to
WhatsApp. This is useful for checking the chatbot's answers and language
support.

Open a terminal in the project folder and run:

Step 1: Install the required packages
pip install -r requirements.txt
Step 2: Set your Groq API key
On Windows Command Prompt:

set GROQ_API_KEY=gsk_your_key_here
On macOS or Linux:

export GROQ_API_KEY=gsk_your_key_here
Replace gsk_your_key_here with your actual Groq API key.

Step 3: Start the local test
python test_local.py
You can now enter questions in the terminal.

Try these example messages:

hi

5 -- to open the dress code menu

Can I wear jeans?

SSD టోకెన్లు ఎప్పుడు వస్తాయి?

The last example is a Telugu question. The chatbot should respond in
Telugu.

8. Add or update information in the knowledge base
The chatbot's information is stored in knowledge_base.py. You can add
new questions and answers whenever you need to expand its knowledge.

Open knowledge_base.py in your code editor.

Find the relevant category, such as darshan or rules.

Locate that category's qas list.

Add a new question-and-answer entry using this format:

{
    "q": "Your new question here?",
    "a": "Your new answer here."
},
Save the file.

Upload and push the updated file to GitHub.

Render will detect the new commit and redeploy the application
automatically.

Because the information is stored in a Python file, you do not need to
perform database migrations.

9. Troubleshooting
If the chatbot does not work as expected, check the following common
problems.

Problem What to check

Meta webhook verification fails Make sure the VERIFY_TOKEN value
in Render exactly matches the value
entered in Meta. The value is
case-sensitive.

The bot does not reply Open your Render service and check
the Logs tab for errors. Also
confirm that you subscribed to the
messages webhook field in Meta.

The bot says "AI brain is not Check whether GROQ_API_KEY is
configured" present and correct in Render's
Environment settings.

The first reply is slow after a The Render free service may have
period of inactivity gone to sleep. It can take around
30--50 seconds to start again.

When troubleshooting, check the Render logs first. They can help you
identify whether the problem is related to the Flask application, an
environment variable, or the WhatsApp connection.

10. Project summary
Sudarshan AI is a bilingual WhatsApp assistant designed to make useful
TTD information easier for pilgrims to access.

The project uses:

Python and Flask for the chatbot application and webhook.

knowledge_base.py to store pilgrim questions and answers
without a separate database.

Groq to help generate natural-language responses.

Render to host the application.

Meta WhatsApp Cloud API to receive and send WhatsApp messages.

Gunicorn to run the Flask application in production.

The setup described in this guide uses the free tiers of the listed
services where available. Actual availability, limits, token
requirements, and pricing are controlled by the service providers and
may change.

🙏 Om Namo Venkatesaya!

