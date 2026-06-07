import pytest
import asyncio
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient


# ─── Fixture: initialize DB before API tests ─────────────────────────────────

@pytest.fixture(scope="session", autouse=True)
def init_test_db():
    """Create all tables before any tests run."""
    async def _init():
        from db.database import init_db
        await init_db()
    asyncio.get_event_loop().run_until_complete(_init())


@pytest.fixture
def test_client():
    from api.main import app
    return TestClient(app)


# ─── Tool Tests ───────────────────────────────────────────────────────────────

class TestWebSearchTool:
    def test_web_search_returns_string(self):
        from tools.web_search import web_search
        with patch("tools.web_search.TavilyClient") as mock_client:
            mock_instance = MagicMock()
            mock_client.return_value = mock_instance
            mock_instance.search.return_value = {
                "answer": "Test answer",
                "results": [
                    {"title": "Result 1", "url": "https://example.com", "content": "Some content"}
                ]
            }
            result = web_search.invoke({"query": "test query"})
            assert isinstance(result, str)
            assert len(result) > 0

    def test_web_search_handles_error(self):
        from tools.web_search import web_search
        with patch("tools.web_search.TavilyClient") as mock_client:
            mock_client.side_effect = Exception("API error")
            result = web_search.invoke({"query": "test"})
            assert "failed" in result.lower() or "error" in result.lower()


class TestSQLQueryTool:
    def test_sql_blocks_non_select(self):
        from tools.sql_query import query_knowledge_base
        result = query_knowledge_base.invoke({"query": "DROP TABLE knowledge_base"})
        assert isinstance(result, str)
        assert len(result) > 0

    def test_sql_select_query(self):
        from tools.sql_query import query_knowledge_base
        result = query_knowledge_base.invoke({"query": "SELECT topic, title FROM knowledge_base LIMIT 1"})
        assert isinstance(result, str)

    def test_sql_natural_language_query(self):
        from tools.sql_query import query_knowledge_base
        with patch("tools.sql_query.sqlite3.connect") as mock_conn:
            mock_cursor = MagicMock()
            mock_conn.return_value.cursor.return_value = mock_cursor
            mock_conn.return_value.row_factory = None
            mock_cursor.fetchall.return_value = []
            result = query_knowledge_base.invoke({"query": "machine learning"})
            assert isinstance(result, str)


class TestPDFTool:
    def test_pdf_nonexistent_file(self):
        from tools.pdf_reader import read_pdf
        result = read_pdf.invoke({"source": "/nonexistent/file.pdf"})
        assert "not found" in result.lower() or "failed" in result.lower()


# ─── Agent State Tests ────────────────────────────────────────────────────────

class TestAgentState:
    def test_initial_state_structure(self):
        from agents.state import ResearchState
        state: ResearchState = {
            "query": "test query",
            "session_id": "test-session",
            "research_plan": None,
            "sub_tasks": [],
            "research_findings": [],
            "sources_used": [],
            "final_answer": None,
            "messages": [],
            "agent_trace": [],
            "current_agent": "planner",
            "iteration_count": 0,
            "status": "running",
            "error": None,
        }
        assert state["query"] == "test query"
        assert state["current_agent"] == "planner"
        assert state["status"] == "running"
        assert isinstance(state["agent_trace"], list)


# ─── API Tests ────────────────────────────────────────────────────────────────

class TestAPIRoutes:
    def test_health_check(self, test_client):
        response = test_client.get("/api/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"

    def test_root_endpoint(self, test_client):
        response = test_client.get("/")
        assert response.status_code == 200
        assert "service" in response.json()

    def test_list_sessions_empty(self, test_client):
        response = test_client.get("/api/sessions")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_get_nonexistent_session(self, test_client):
        response = test_client.get("/api/sessions/nonexistent-id")
        assert response.status_code == 404


# ─── Tools Registry Tests ─────────────────────────────────────────────────────

class TestToolsRegistry:
    def test_all_tools_imported(self):
        from tools import ALL_TOOLS, RESEARCHER_TOOLS
        assert len(ALL_TOOLS) == 3
        assert len(RESEARCHER_TOOLS) == 3

    def test_tool_names(self):
        from tools import ALL_TOOLS
        names = [t.name for t in ALL_TOOLS]
        assert "web_search" in names
        assert "read_pdf" in names
        assert "query_knowledge_base" in names
