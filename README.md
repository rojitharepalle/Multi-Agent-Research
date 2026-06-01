# 🤖 Multi-Agent Research System

A production-grade multi-agent AI application featuring tool calling, real-time streaming, and a modern React dashboard.

## Architecture

User (React UI)
↕ WebSocket
FastAPI Backend
↕
LangGraph Orchestrator
├── Planner Agent    — analyzes query, breaks into sub-tasks
├── Researcher Agent — web search, PDF reader, SQL query tools
└── Writer Agent     — synthesizes findings into final answer
↕
SQLite + ChromaDB (session storage + vector memory)

---

## 🧰 Tech Stack

| Layer | Technology |
|---|---|
| Orchestration | LangGraph |
| LLM | OpenAI GPT-4o |
| Tools | Tavily (web search), PyMuPDF (PDF), SQLite |
| Backend | FastAPI + WebSockets |
| Frontend | React + TailwindCSS + Zustand |
| Deploy | Docker + GitHub Actions + HuggingFace Spaces |

---

## 📁 Project Structure

multi-agent-research/
├── backend/
│   ├── agents/
│   │   ├── state.py         # Shared LangGraph state
│   │   ├── planner.py       # Planner agent
│   │   ├── researcher.py    # Researcher agent with tool calling
│   │   ├── writer.py        # Writer agent
│   │   └── pipeline.py      # LangGraph graph wiring
│   ├── tools/
│   │   ├── web_search.py    # Tavily web search tool
│   │   ├── pdf_reader.py    # PyMuPDF PDF reader tool
│   │   └── sql_query.py     # SQLite knowledge base tool
│   ├── api/
│   │   ├── main.py          # FastAPI app entry point
│   │   ├── routes.py        # REST endpoints
│   │   └── websocket.py     # WebSocket streaming endpoint
│   ├── core/
│   │   ├── config.py        # Pydantic settings
│   │   └── logging.py       # Logging setup
│   ├── db/
│   │   └── database.py      # SQLAlchemy async models
│   ├── tests/
│   │   └── test_agents.py   # Unit tests
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── SearchBar.jsx       # Query input
│   │   │   ├── TracePanel.jsx      # Live agent trace
│   │   │   ├── AgentEventCard.jsx  # Individual event cards
│   │   │   ├── AnswerPanel.jsx     # Final answer with markdown
│   │   │   └── HistoryPanel.jsx    # Session history
│   │   ├── hooks/
│   │   │   └── useResearchWebSocket.js  # WebSocket hook
│   │   ├── store/
│   │   │   └── researchStore.js    # Zustand state store
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── index.css
│   ├── Dockerfile
│   ├── nginx.conf
│   ├── package.json
│   └── vite.config.js
├── .github/
│   └── workflows/
│       └── ci-cd.yml        # GitHub Actions pipeline
├── docker-compose.yml
└── README.md

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 20+
- OpenAI API key
- Tavily API key (free at tavily.com)

### Backend Setup

```bash
cd backend
cp .env.example .env
# Fill in your API keys in .env

python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

uvicorn api.main:app --reload
# API running at http://localhost:8000
# Docs at http://localhost:8000/docs
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
# UI running at http://localhost:5173
```

### Docker (Full Stack)

```bash
cp backend/.env.example backend/.env
# Fill in your API keys

docker-compose up --build
# App running at http://localhost:80
```

---

## 🔑 Environment Variables

Create `backend/.env` from `backend/.env.example`:

```env
OPENAI_API_KEY=sk-...
TAVILY_API_KEY=tvly-...
DATABASE_URL=sqlite+aiosqlite:///./research.db
CHROMA_PERSIST_DIR=./chroma_db
ENVIRONMENT=development
LOG_LEVEL=INFO
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

---

## 🤖 How It Works

1. **User submits a query** via the React UI
2. **WebSocket connection** opens between frontend and FastAPI
3. **Planner Agent** analyzes the query and creates a research plan with 2-4 sub-tasks
4. **Researcher Agent** executes each sub-task using tools:
   - `web_search` — searches the web via Tavily API
   - `read_pdf` — extracts text from PDF files or URLs
   - `query_knowledge_base` — queries internal SQLite database
5. **Writer Agent** synthesizes all findings into a structured markdown answer
6. **Each agent event streams live** to the React frontend via WebSocket
7. **Session is persisted** to SQLite for history

---

## 🧪 Running Tests

```bash
cd backend
source venv/bin/activate
pytest tests/ -v
```

---

## 🚢 Deployment

### GitHub Actions CI/CD

On every push to `main`:
1. Runs backend tests
2. Builds frontend
3. Builds and pushes Docker images to GitHub Container Registry
4. Deploys to HuggingFace Spaces

### Required GitHub Secrets

| Secret | Description |
|---|---|
| `OPENAI_API_KEY` | OpenAI API key |
| `TAVILY_API_KEY` | Tavily search API key |
| `HF_TOKEN` | HuggingFace access token |
| `HF_SPACE` | HuggingFace space name (e.g. `username/multi-agent-research`) |
