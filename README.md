# 🧠 Customer Sentiment Watchdog — Hackathon Project 🧠

## 🚀 Problem Statement:  
###  Customer Sentiment Watchdog for Support Teams**

> _"It’s hard for CX teams to detect rising frustration or satisfaction trends across support channels (emails, chats, tickets)."_  

## 💡 Our Solution:

We built an **AI-powered dashboard** that analyzes customer feedback in real-time (from web forms, emails, and tickets), classifies emotional tone (positive, neutral, negative), and **alerts the team if negative sentiment spikes**.

Our virtual AI assistant, **LIZA**, provides real-time suggestions based on recent complaints using LLMs (via Sarvam AI/OpenRouter API).

---

## 🛠️ Key Features

✅ Sentiment analysis from feedback  
✅ Visual analytics (charts for sentiment, activity, top complaints)  
✅ Chat-based assistant “LIZA” for suggestions  
✅ Live feedback stream  
✅ Tracks engagement levels: Promoters, Passives, Detractors  
✅ Clean Tailwind + Chart.js frontend  
✅ Full Flask backend with CSV-based feedback storage  

---

## 🤖 Tech Stack

- **Frontend:** HTML, TailwindCSS, Chart.js  
- **Backend:** Python, Flask  
- **AI Integration:** Sarvam AI via OpenRouter API (used in `suggestion_agent.py`)  
- **Data Handling:** pandas, CSV  
- **Hosting Ready:** Portable for deployment on Render/Heroku/Localhost  

---

## 💬 What We Learned

This was a 3-day intense hackathon where:
- We **used AI responsibly** — yes, we took help, but we **engineered prompts**, debugged countless errors, iterated fast, and learned deeply.
- We explored **prompt-tuning**, **model handling**, **backend integration**, and **frontend polish**.
- I made mistakes, learned from them, and gave this project my 💯 percent.
- The biggest takeaway: **how to use AI tools _efficiently_** to solve real problems.

> _We hope you like our project as much as we loved building it._ 💜

---

## 📦 Folder Structure
📁 project-root
│
├── app.py # Main Flask server
├── feedback.csv # Stores all feedback data
├── suggestion_agent.py # AI generation using Sarvam AI
├── sentiment_agent.py # Handles sentiment classification
├── feedback_handler.py # Handles data saving
├── chart_generator.py # Prepares data for frontend
│
├── templates/
│ ├── insights.html # Dashboard (main)
│ ├── index.html # Web feedback form
│ ├── ticket.html # Ticket feedback form
│ └── email.html # Email feedback form

yaml
Copy
Edit


---
## 👥 Team Contribution
This project is my solo submission for a hackathon, built with:

AI support (Sarvam, ChatGPT, etc.)

My own full-stack implementation

3 days of hands-on effort, learning, debugging, and improving every module

## 🌟 Final Words
This was not just a project, but a learning journey.
From prompt engineering to building a full-stack AI tool, this experience helped me grow immensely as a developer and a problem-solver.

Thank you for checking it out. ❤️


## 📋 Requirements

Install these using `pip install -r requirements.txt`

```txt
Flask
pandas
requests

# Step 1: Clone this repo
git clone https://github.com/MeNoodie/customer_sentiment.project.git
cd sentiment-watchdog

# Step 2: Create virtual env (optional)
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Step 3: Install dependencies
pip install -r requirements.txt

# Step 4: Run the app
python app.py


headers = {
    "Authorization": "Bearer YOUR_OPENROUTER_API_KEY",
    "Content-Type": "application/json"
}




