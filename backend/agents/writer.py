from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from agents.state import ResearchState, AgentEvent
from core.config import settings
from core.logging import logger
from datetime import datetime


WRITER_SYSTEM_PROMPT = """You are a Research Writer Agent. Synthesize research findings into a clear, well-structured answer.

Guidelines:
- Use markdown formatting with headers and bullet points
- Include specific facts and data from the research
- Be comprehensive but concise
- End with key takeaways"""


def writer_agent(state: ResearchState) -> ResearchState:
    logger.info(f"[Writer] Synthesizing {len(state.get('research_findings', []))} findings")

    llm = ChatGroq(
        model=settings.groq_model,
        api_key=settings.groq_api_key,
        temperature=0.3,
    )

    trace_events: list[AgentEvent] = [{
        "type": "agent_start",
        "agent": "writer",
        "content": "Synthesizing research findings into final answer...",
        "tool_name": None,
        "tool_input": None,
        "timestamp": datetime.utcnow().isoformat(),
    }]

    try:
        findings_text = "\n\n---\n\n".join(
            f"Finding {i+1}:\n{f}"
            for i, f in enumerate(state.get("research_findings", []))
        )

        sources_text = "\n".join(f"- {s}" for s in state.get("sources_used", []))

        messages = [
            SystemMessage(content=WRITER_SYSTEM_PROMPT),
            HumanMessage(content=f"""Original Query: {state['query']}

Research Findings:
{findings_text}

Sources Used:
{sources_text or 'Web search and knowledge base'}

Synthesize these findings into a comprehensive answer."""),
        ]

        response = llm.invoke(messages)
        final_answer = response.content

        logger.info(f"[Writer] Final answer generated ({len(final_answer)} chars)")

        trace_events.append({
            "type": "agent_end",
            "agent": "writer",
            "content": "Final answer ready.",
            "tool_name": None,
            "tool_input": None,
            "timestamp": datetime.utcnow().isoformat(),
        })

        return {
            **state,
            "final_answer": final_answer,
            "current_agent": "done",
            "status": "completed",
            "agent_trace": trace_events,
            "messages": list(state.get("messages", [])) + messages + [response],
        }

    except Exception as e:
        logger.error(f"[Writer] Failed: {e}")
        trace_events.append({
            "type": "error",
            "agent": "writer",
            "content": f"Writer failed: {str(e)}",
            "tool_name": None,
            "tool_input": None,
            "timestamp": datetime.utcnow().isoformat(),
        })
        return {
            **state,
            "final_answer": f"Research completed but synthesis failed: {str(e)}",
            "current_agent": "done",
            "status": "failed",
            "agent_trace": trace_events,
            "error": str(e),
        }
