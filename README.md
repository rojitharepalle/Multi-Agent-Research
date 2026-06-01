# 🤖 Multi-Agent Research System

A production-grade multi-agent AI application featuring tool calling, real-time streaming, and a modern React dashboard.

## Architecture

    User (React UI)
         ↕ WebSocket
    FastAPI Backend
         ↕
    LangGraph Orchestrator
         ├── Planner Agent    — breaks query into sub-tasks
         ├── Researcher Agent — web search, PDF reader, SQL query
         └── Writer Agent     — synthesizes final answer
         ↕
    SQLite + ChromaDB

## Tech Stack

| Layer         | Technology                        |
|---------------|-----------------------------------|
| Orchestration | LangGraph                         |
| LLM           | OpenAI GPT-4o                     |
| Tools         | Tavily, PyMuPDF, SQLite           |
| Backend       | FastAPI + WebSockets              |
| Frontend      | React + TailwindCSS + Zustand     |
| Deploy        | Docker + GitHub Actions           |

## Project Structure

```
multi-agent-research/
├── backend/
│   ├── agents/
│   │   ├── state.py          - Shared LangGraph state
│   │   ├── planner.py        - Planner agent
│   │   ├── researcher.py     - Researcher agent with tool calling
│   │   ├── writer.py         - Writer agent
│   │   └── pipeline.py       - LangGraph graph wiring
│   ├── tools/
│   │   ├── web_search.py     - Tavily web search tool
│   │   ├── pdf_reader.py     - PyMuPDF PDF reader tool
│   │   └── sql_query.py      - SQLite knowledge base tool
│   ├── api/
│   │   ├── main.py           - FastAPI app entry point
│   │   ├── routes.py         - REST endpoints
│   │   └── websocket.py      - WebSocket streaming endpoint
│   ├── core/
│   │   ├── config.py         - Pydantic settings
│   │   └── logging.py        - Logging setup
│   ├── db/
│   │   └── database.py       - SQLAlchemy async models
│   ├── tests/
│   │   └── test_agents.py    - Unit tests
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── SearchBar.jsx
│   │   │   ├── TracePanel.jsx
│   │   │   ├── AgentEventCard.jsx
│   │   │   ├── AnswerPanel.jsx
│   │   │   └── HistoryPanel.jsx
│   │   ├── hooks/
│   │   │   └── useResearchWebSocket.js
│   │   ├── store/
│   │   │   └── researchStore.js
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── index.css
│   ├── Dockerfile
│   ├── nginx.conf
│   ├── package.json
│   └── vite.config.js
├── .github/
│   └── workflows/
│       └── ci-cd.yml
├── docker-compose.yml
└── README.md
```

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 20+
- OpenAI API key
- Tavily API key (free at tavily.com)

### Backend Setup

    cd backend
    cp .env.example .env
    source venv/bin/activate
    pip install -r requirements.txt
    uvicorn api.main:app --reload

### Frontend Setup

    cd frontend
    npm install
    npm run dev

### Docker

    docker-compose up --build

## Environment Variables

    OPENAI_API_KEY=sk-...
    TAVILY_API_KEY=tvly-...
    DATABASE_URL=sqlite+aiosqlite:///./research.db
    CHROMA_PERSIST_DIR=./chroma_db
    ENVIRONMENT=development
    LOG_LEVEL=INFO
    CORS_ORIGINS=http://localhost:5173,http://localhost:3000

## How It Works

1. User submits a query via the React UI
2. WebSocket connection opens between frontend and FastAPI
3. Planner Agent analyzes the query and creates a research plan with 2-4 sub-tasks
4. Researcher Agent executes each sub-task using tools
   - web_search  : searches the web via Tavily API
   - read_pdf    : extracts text from PDF files or URLs
   - query_knowledge_base : queries internal SQLite database
5. Writer Agent synthesizes all findings into a structured markdown answer
6. Each agent event streams live to the React frontend via WebSocket
7. Session is persisted to SQLite for history

## Running Tests

    cd backend
    source venv/bin/activate
    pytest tests/ -v

## Deployment

On every push to main, GitHub Actions will:
1. Run backend tests
2. Build frontend
3. Build and push Docker images to GitHub Container Registry
4. Deploy to HuggingFace Spaces

### Required GitHub Secrets

| Secret          | Description                          |
|-----------------|--------------------------------------|
| OPENAI_API_KEY  | OpenAI API key                       |
| TAVILY_API_KEY  | Tavily search API key                |
| HF_TOKEN        | HuggingFace access token             |
| HF_SPACE        | HuggingFace space name               |

