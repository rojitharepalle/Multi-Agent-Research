from langgraph.graph import StateGraph, END
from agents.state import ResearchState
from agents.planner import planner_agent
from agents.researcher import researcher_agent
from agents.writer import writer_agent
from core.logging import logger
import uuid


def build_research_graph():
    graph = StateGraph(ResearchState)

    graph.add_node("planner", planner_agent)
    graph.add_node("researcher", researcher_agent)
    graph.add_node("writer", writer_agent)

    graph.set_entry_point("planner")
    graph.add_edge("planner", "researcher")
    graph.add_edge("researcher", "writer")
    graph.add_edge("writer", END)

    return graph.compile()


research_graph = build_research_graph()


async def run_research_pipeline(
    query: str,
    session_id: str = None,
    on_event=None,
) -> ResearchState:
    if not session_id:
        session_id = str(uuid.uuid4())

    initial_state: ResearchState = {
        "query": query,
        "session_id": session_id,
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

    logger.info(f"[Pipeline] Starting session {session_id}: {query[:80]}")

    final_state = initial_state

    async for chunk in research_graph.astream(initial_state):
        for node_name, node_state in chunk.items():
            logger.debug(f"[Pipeline] Node '{node_name}' completed")
            final_state = {**final_state, **node_state}

            if on_event and node_state.get("agent_trace"):
                for event in node_state["agent_trace"]:
                    await on_event(event)

    logger.info(f"[Pipeline] Session {session_id} status: {final_state.get('status')}")
    return final_state
