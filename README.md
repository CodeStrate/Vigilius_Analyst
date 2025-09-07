# 📊 Vigilius Analyst

[![Python 3.12.9+](https://img.shields.io/badge/python-≥3.12.9-blue.svg)](https://www.python.org/downloads/release/python-3129/)  
[![Conda](https://img.shields.io/badge/conda-ready-green.svg)](https://docs.conda.io/en/latest/)

An intelligent **data analysis assistant** built with **Streamlit** and **LangGraph**/**Langchain**.  
Vigilius lets you query datasets in **natural language**, automatically generating SQL, visualizations, and insights — all powered by multiple AI providers.

---

## 🚀 Key Features

- 🔗 **Multi-Provider AI Support**: OpenAI, Groq, Gemini, and Ollama  
- 🧠 **Smart SQL Agent**: Generates, validates, and executes SQL from natural language  
- 💬 **Data Assistant**: Handles small talk & intent classification  
- 📂 **Multiple File Formats**: CSV, Excel, and SQLite database support  
- ⚡ **Streaming Responses**: Real-time answers with clean formatting  
- 💾 **Session Management**: Persistent chat history (Graph CheckPointer) & model configs

---

## 📁 Project Structure

Based on the [`sql-agent`](https://github.com/CodeStrate/Vigilius_Analyst/tree/sql-agent) branch:  

```
Vigilius_Analyst/
├── agent/
│   ├── agent_handler.py         # Core SQL agent logic
│   ├── data_assistant_handler.py # Intent classification + small talk
│   ├── llm_factory.py           # Multi-provider LLM factory
│   └── prompts.py               # Agent system prompts
│
├── assets/
│   └── chat_icons/              # User & bot avatars
│
├── backend/                     # FastAPI backend (future scope)
│
├── datasets/                    # Uploaded and processed datasets
│
├── debug/
│   └── check_agent.py           # CLI testing tool for agents
│
├── prebuilt/
│   └── react_sql_agent.py       # LangGraph ReAct SQL agent template
│
├── utils/
│   ├── ai_providers.py          # Provider configs + available models
│   ├── app_utils.py             # Streamlit utilities
│   └── misc_utils.py            # General helper functions
│
├── .env                         # env file for API Keys (More in future)
├── agent_graph.png              # Mermaid Image for Agent Graph Architecture
├── app.py                       # Streamlit frontend entrypoint
├── requirements.txt             # Python dependencies
└── README.md
```

---

## ⚙️ Setup Instructions

### Requirements
- **Python** ≥ 3.12.9  
- Works on macOS, Linux, Windows  

### Option 1: Virtualenv
```bash
git clone https://github.com/CodeStrate/Vigilius_Analyst.git
cd Vigilius_Analyst
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Option 2: Conda
```bash
git clone https://github.com/CodeStrate/Vigilius_Analyst.git
cd Vigilius_Analyst
conda create -n vigilius python=3.12.9
conda activate vigilius
pip install -r requirements.txt
```

### Configure Environment
Create a `.env` file with your keys:

```ini
# AI Provider Keys
OPENAI_API_KEY=your_openai_key
GROQ_API_KEY=your_groq_key
GEMINI_API_KEY=your_gemini_key

# Ollama requires no API key (runs locally)
# Install from: https://ollama.com/download
```

### (Optional) Install Ollama Models
```bash
ollama pull llama3:8b
```

---

## ▶️ Running Vigilius

**Web App (Streamlit)**
```bash
streamlit run app.py
```

**Terminal Debugging**
```bash
python -m debug.check_agent
```

---

## 🎯 Usage Guide

1. **Upload Your Dataset**  
   - Supported: CSV, Excel (.xlsx), SQLite (.db)  
   - Files are converted to SQLite + schema analyzed  

2. **Select Models**  
   - Choose AI providers + models for SQL Agent & Data Assistant  
   - Confirm selection to initialize  

3. **Chat with Your Data**  
   - Example queries:  
     - “Top 10 customers by sales”  
     - “Revenue trends by month”  
     - “Most popular products”  

4. **Get Results**  
   - Auto-generated SQL → executed on database  
   - Outputs as tables (whenever available, pandas WIP)
   - Streaming responses with formatting  

---

## 🧩 AI Agent Architecture

### SQL Agent
- Schema discovery  
- Query generation + validation  
- Results formatting  

### Data Assistant
- Handles non-data queries  
- Classifies and validates intent (SQL vs. small talk)  
- Maintains conversation flow  

### LLM Factory
- Unified interface for all providers  
- Dynamic model switching  
- Provider-specific optimizations  

---

## 🔧 Configuration

| Provider  | Models | Best For |
|-----------|--------|----------|
| **OpenAI** | GPT-4, GPT-3.5 | High accuracy, complex queries |
| **Groq**   | Llama-3, Mixtral | Ultra-fast inference |
| **Gemini** | Gemini-Pro | Google’s latest models |
| **Ollama** | Llama3, Mistral, CodeLlama | Local, private, free |

- Edit prompts → `agent/prompts.py`  
- Adjust model configs → `agent/llm_factory.py`  
- UI tweaks → `app.py`  

---

## 🧪 Testing

**CLI Debugging**
```bash
python -m debug.check_agent
```

---

## 🛠️ Future Roadmap

- ✅ FastAPI backend (multi-user, sessions, API access)  
- ✅ Persistent chat history  
- ✅ Export results (CSV, Excel, PDF)  
- ✅ Advanced visualizations + customization  
- ✅ Scheduled reports + notifications  

---

## 🤝 Contributing

1. Fork this repo  
2. Create a branch (`git checkout -b feature/your-feature`)  
3. Commit (`git commit -m "Add your feature"`)  
4. Push (`git push origin feature/your-feature`)  
5. Open a Pull Request  

---

## 📞 Support

For help or feature requests, please [open an issue](../../issues).  
