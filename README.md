# 🧠 OnlineChatBot

An end-to-end chatbot web application built with **FastAPI**, **Prisma for Python**, and **Streamlit**. The backend supports user authentication, chat management, speech-to-text processing, and integrates ngrok for secure local development exposure.

---

## 📁 Project Structure

```
OnlineChatbot/
├── assets/                  # Static assets for UI (e.g., bot/user icons)
├── backend/
│   ├── models/              # Pydantic models for API
│   ├── routes/              # FastAPI route handlers
│   └── main.py              # Backend entrypoint with ngrok tunnel and lifespan management
├── datasets/
│   └── uploaded_dataset.db  # Local SQLite DB (used to store data temporarily to query using Streamlit UI)
├── handlers/
│   ├── chat_handler.py      # Main chat logic
│   ├── chat_history_handler.py # Chat history management
│   └── stt_handler.py       # Speech-to-text handling
├── prisma/
│   ├── migrations/          # Prisma migration files
│   └── schema.prisma        # Prisma schema (Python-compatible)
├── utils/
│   ├── app_utils.py         # Util Functions used by `app.py`
│   ├── db_dependency.py     # FastAPI DB dependency injection
│   └── utils.py             # General utilities
├── app.py                   # Streamlit frontend
├── config.yaml              # Configuration YAML for SQLite
├── .env                     # Environment variables
├── requirements.txt         # Python dependencies
└── README.md
```

---

## 🚀 Setup Instructions

### 1. Clone & Install Requirements
- Ensure python > 3.11 for this project.
```bash
git clone https://github.com/vDoIT-Technologies/online-nlp-chatbot-backend.git 
cd ONLINECHATBOT
python -m venv venv
source venv/bin/activate  # Or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
```

### 2. Configure `.env`

Set the following variables in your `.env` file:

```ini
DATABASE_URL="mysql://<user>:<password>@localhost:3306/chatdb"
NGROK_AUTH_TOKEN=your_token_here
BACKEND_PORT=8000
```

---

## 🗄️ Database Setup (MySQL)

### Create a user with limited privileges:

```sql
CREATE USER 'prisma'@'localhost' IDENTIFIED BY 'yourpassword';
GRANT CREATE, SELECT, INSERT, UPDATE, DELETE ON *.* TO 'prisma'@'localhost';
```

Then:

1. Generate Prisma Client

```bash
prisma generate
```

2. Deploy migrations or push migrations to DB

```bash
prisma db push
```

> Make sure `prisma.schema` has valid models and the `DATABASE_URL` is set in `.env`.

---

## 🔌 Running the Backend with ngrok (in project root)

```bash
uvicorn backend.main:app --port 8000 --reload
```

✅ Starts FastAPI on `localhost:8000`  
🌐 ngrok tunnel is created and displayed in logs

---

## 🔐 Authentication

- `POST /api/v1/signup`: Register a user

- `POST /api/v1/login`: Login with email & password
  - Returns `401 Unauthorized` on wrong credentials
  - Ensures email uniqueness (both at DB + API level)
  - Passwords must be **8+ characters, alphanumeric**

---

## 🧠 Chat Features

- Speech-to-Text (via `handlers/stt_handler.py`)
- Persistent chat history
- Clean UI with avatars via `assets/chat_icons`

---

## 🧪 API Docs

Visit [http://localhost:8000/docs](http://localhost:8000/docs) (or your ngrok URL) for interactive Swagger UI.

---

## 🛠️ Dev Notes

- `orm_mode` in Pydantic models has been replaced by `ConfigDict`.
- Prisma for Python currently lacks some features like shadow DB. Use `db push` and manual migrations.
- Routes expect valid JSON; missing payloads result in `422`.
