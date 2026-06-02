from langchain_core.tools import tool
from core.logging import logger
import sqlite3
import json
import re


def get_sync_db_path() -> str:
    from core.config import settings
    url = settings.database_url
    path = url.replace("sqlite+aiosqlite:///", "").replace("sqlite:///", "")
    return path


@tool
def query_knowledge_base(query: str) -> str:
    """
    Search the internal knowledge base using natural language or SQL.
    Use this to find information stored in our research database.
    Supports both keyword search and direct SQL SELECT queries.

    Args:
        query: Natural language question or SQL SELECT statement

    Returns:
        Matching records from the knowledge base as formatted text
    """
    try:
        db_path = get_sync_db_path()
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        is_sql = query.strip().upper().startswith("SELECT")

        if is_sql:
            if not re.match(r"^\s*SELECT\b", query.strip(), re.IGNORECASE):
                return "Only SELECT queries are permitted for safety."
            cursor.execute(query)
        else:
            keywords = [w for w in query.lower().split() if len(w) > 3]
            if not keywords:
                keywords = [""]

            conditions = " OR ".join(
                ["LOWER(title) LIKE ? OR LOWER(summary) LIKE ? OR LOWER(topic) LIKE ?"]
                * len(keywords)
            )
            params = []
            for kw in keywords[:5]:
                params.extend([f"%{kw}%", f"%{kw}%", f"%{kw}%"])

            sql = f"""
                SELECT topic, title, summary, tags
                FROM knowledge_base
                WHERE {conditions}
                LIMIT 10
            """
            cursor.execute(sql, params)

        rows = cursor.fetchall()
        conn.close()

        if not rows:
            return f"No records found in knowledge base for: {query}"

        results = [f"Knowledge Base Results ({len(rows)} found)\n"]
        for row in rows:
            row_dict = dict(row)
            tags = row_dict.get("tags", "[]")
            if isinstance(tags, str):
                try:
                    tags = json.loads(tags)
                except Exception:
                    tags = []
            results.append(
                f"Title: {row_dict.get('title', 'Untitled')} [{row_dict.get('topic', '')}]\n"
                f"Summary: {row_dict.get('summary', '')}\n"
                f"Tags: {', '.join(tags) if tags else 'none'}\n"
            )

        logger.info(f"Knowledge base query returned {len(rows)} results")
        return "\n".join(results)

    except Exception as e:
        logger.error(f"SQL query failed: {e}")
        return f"Knowledge base query failed: {str(e)}"
