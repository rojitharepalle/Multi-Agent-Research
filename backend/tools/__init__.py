from tools.web_search import web_search
from tools.pdf_reader import read_pdf
from tools.sql_query import query_knowledge_base

ALL_TOOLS = [web_search, read_pdf, query_knowledge_base]
RESEARCHER_TOOLS = [web_search, read_pdf, query_knowledge_base]

__all__ = ["web_search", "read_pdf", "query_knowledge_base", "ALL_TOOLS", "RESEARCHER_TOOLS"]
