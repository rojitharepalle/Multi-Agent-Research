from typing import TypedDict, Annotated, List, Optional, Any
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage
import operator


class AgentEvent(TypedDict):
    type: str
    agent: str
    content: str
    tool_name: Optional[str]
    tool_input: Optional[Any]
    timestamp: str


class ResearchState(TypedDict):
    query: str
    session_id: str
    research_plan: Optional[str]
    sub_tasks: List[str]
    research_findings: List[str]
    sources_used: List[str]
    final_answer: Optional[str]
    messages: Annotated[List[BaseMessage], add_messages]
    agent_trace: Annotated[List[AgentEvent], operator.add]
    current_agent: str
    iteration_count: int
    status: str
    error: Optional[str]
