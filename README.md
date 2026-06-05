# 🌐 AI Atlas

> A smart, free AI-powered study and life assistant — built with Groq, LangGraph, Streamlit, and DuckDuckGo fallback. No OpenAI. No payments. Just answers.

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.x-red?style=flat-square&logo=streamlit)
![Groq](https://img.shields.io/badge/Groq-Free_API-orange?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

---

## 🧠 What is AI Atlas?

**AI Atlas** (formerly Study Buddy AI) is a conversational AI assistant that can help you with:

- 📚 Study plans, exam prep, and learning guidance
- 💼 Career advice, resume writing, and project planning
- 🧘 Mental health support and wellness tips
- 💻 Tech topics — ML, AI, NLP, APIs, databases, and more
- 🌍 General knowledge across science, health, and everyday life

It understands abbreviations like `ML`, `NLP`, `DS`, `API` natively — no need to spell everything out.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🤖 Groq-powered AI | Uses `llama3-70b-8192` via free Groq API |
| 🔁 Conversation memory | Maintains context across multi-turn chats |
| 🔤 Abbreviation expander | Understands ML, AI, NLP, DS, CV, OOP, etc. |
| 🌐 DuckDuckGo fallback | Answers even if API is unavailable |
| 🎨 Clean chat UI | ChatGPT-style Streamlit interface |
| ⚡ FastAPI backend | Optional REST API via `server.py` |

---

## 🗂️ Project Structure

```
AI_Atlas/
│
├── agent.py                  # Core AI logic — Groq API + fallback
├── capstone_streamlit.py     # Streamlit chat UI (main app)
├── capstone.py               # Alternate entry point
├── server.py                 # FastAPI REST backend
├── requirements.txt          # Python dependencies
├── .env                      # API keys (not committed)
├── .env.example              # Template for environment variables
│
└── web/                      # Optional vanilla JS frontend
    ├── index.html
    ├── app.js
    └── styles.css
```

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/AI-Atlas.git
cd AI-Atlas
```

### 2. Create and activate a virtual environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up your free Groq API key

Get a free key at [console.groq.com](https://console.groq.com) — no payment required.

Create a `.env` file in the root folder:

```env
GROQ_API_KEY=your_groq_api_key_here
```

### 5. Run the app

```bash
streamlit run capstone_streamlit.py
```

Open your browser at `http://localhost:8501` 🎉

---

## 🔌 Optional: Run the FastAPI backend

In a separate terminal (with venv activated):

```bash
uvicorn server:app --reload
```

API runs at `http://localhost:8000`

---

## 📦 Requirements

```
groq
streamlit
fastapi
uvicorn
python-dotenv
duckduckgo-search
langchain
langgraph
sentence-transformers
```

---

## 🧪 Test Your Setup

Run this in your terminal to verify Groq is working:

```bash
python -c "
from dotenv import load_dotenv; import os; from groq import Groq
load_dotenv()
client = Groq(api_key=os.getenv('GROQ_API_KEY'))
r = client.chat.completions.create(
    model='llama3-70b-8192',
    messages=[{'role':'user','content':'Say hello!'}]
)
print(r.choices[0].message.content)
"
```

---

## 🌐 How It Works

```
User Input
    │
    ▼
Abbreviation Expander (ML → machine learning, etc.)
    │
    ▼
Groq API (llama3-70b-8192) ──── fails? ──► DuckDuckGo Search
    │                                            │
    └──────────────────┬─────────────────────────┘
                       ▼
              Answer returned to UI
```

---

## 🔑 Environment Variables

| Variable | Required | Description |
|---|---|---|
| `GROQ_API_KEY` | ✅ Yes | Free key from console.groq.com |

---

## 🛠️ Troubleshooting

| Problem | Fix |
|---|---|
| `model_decommissioned` error | Make sure model is `llama3-70b-8192` in `agent.py` |
| `API key not found` | Check `.env` is in the root folder |
| DuckDuckGo results instead of AI | Groq API is failing — check your key |
| PowerShell blocks venv activation | Run `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser` |
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` |

---

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first.

1. Fork the repo
2. Create your branch: `git checkout -b feature/your-feature`
3. Commit: `git commit -m "Add your feature"`
4. Push: `git push origin feature/your-feature`
5. Open a Pull Request

---

## 📄 License

MIT License — free to use, modify, and distribute.

---

## 👩‍💻 Author

Built with ❤️ using [Groq](https://console.groq.com) · [Streamlit](https://streamlit.io) · [LangGraph](https://langchain-ai.github.io/langgraph/)