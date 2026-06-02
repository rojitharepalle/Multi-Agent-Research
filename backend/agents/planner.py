from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from agents.state import ResearchState, AgentEvent
from core.config import settings
from core.logging import logger
from datetime import datetime
import json


PLANNER_SYSTEM_PROMPT = """You are a Research Planner Agent. Analyze the user query and break it into 2-4 specific research sub-tasks.

Output ONLY valid JSON in this exact format with no extra text:
{
  "plan_summary": "One-sentence overview of the research approach",
  "sub_tasks": [
    "Search the web for: specific query here",
    "Query knowledge base for: specific topic here"
  ],
  "expected_output": "Description of what the final answer should include"
}"""


def planner_agent(state: ResearchState) -> ResearchState:
    logger.info(f"[Planner] Starting for query: {state['query'][:80]}")

    llm = ChatGroq(
        model=settings.groq_model,
        api_key=settings.groq_api_key,
        temperature=0.1,
    )

    trace_event: AgentEvent = {
        "type": "agent_start",
        "agent": "planner",
        "content": f"Analyzing query: {state['query']}",
        "tool_name": None,
        "tool_input": None,
        "timestamp": datetime.utcnow().isoformat(),
    }

    try:
        messages = [
            SystemMessage(content=PLANNER_SYSTEM_PROMPT),
            HumanMessage(content=f"Research query: {state['query']}"),
        ]

        response = llm.invoke(messages)
        raw = response.content.strip()

        if "```json" in raw:
            raw = raw.split("```json")[1].split("```")[0].strip()
        elif "```" in raw:
            raw = raw.split("```")[1].split("```")[0].strip()

        plan_data = json.loads(raw)
        plan_summary = plan_data.get("plan_summary", "Research plan created")
        sub_tasks = plan_data.get("sub_tasks", [state["query"]])

        logger.info(f"[Planner] Plan: {plan_summary} | {len(sub_tasks)} sub-tasks")

        end_event: AgentEvent = {
            "type": "agent_end",
            "agent": "planner",
            "content": f"Plan: {plan_summary}\n\nSub-tasks:\n" + "\n".join(f"- {t}" for t in sub_tasks),
            "tool_name": None,
            "tool_input": None,
            "timestamp": datetime.utcnow().isoformat(),
        }

        return {
            **state,
            "research_plan": plan_summary,
            "sub_tasks": sub_tasks,
            "current_agent": "researcher",
            "agent_trace": [trace_event, end_event],
            "messages": messages + [response],
        }

    except Exception as e:
        logger.error(f"[Planner] Failed: {e}")
        error_event: AgentEvent = {
            "type": "error",
            "agent": "planner",
            "content": f"Planner failed: {str(e)}. Falling back to direct search.",
            "tool_name": None,
            "tool_input": None,
            "timestamp": datetime.utcnow().isoformat(),
        }
        return {
            **state,
            "research_plan": "Direct research",
            "sub_tasks": [f"Search the web for: {state['query']}"],
            "current_agent": "researcher",
            "agent_trace": [trace_event, error_event],
        }
