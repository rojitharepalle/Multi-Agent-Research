from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage
from agents.state import ResearchState, AgentEvent
from tools import RESEARCHER_TOOLS
from core.config import settings
from core.logging import logger
from datetime import datetime


RESEARCHER_SYSTEM_PROMPT = """You are a Research Agent. You have access to these tools:
- web_search: search the web for current information
- read_pdf: extract text from PDF files or URLs  
- query_knowledge_base: search internal database

For the given research tasks, call the appropriate tools one at a time to gather information.
After gathering enough information, provide a summary of your findings."""


def researcher_agent(state: ResearchState) -> ResearchState:
    logger.info(f"[Researcher] Executing {len(state.get('sub_tasks', []))} sub-tasks")

    llm = ChatGroq(
        model=settings.groq_model,
        api_key=settings.groq_api_key,
        temperature=0.1,
    ).bind_tools(RESEARCHER_TOOLS, tool_choice="auto")

    trace_events: list[AgentEvent] = [{
        "type": "agent_start",
        "agent": "researcher",
        "content": f"Executing plan: {state.get('research_plan', 'Direct research')}",
        "tool_name": None,
        "tool_input": None,
        "timestamp": datetime.utcnow().isoformat(),
    }]

    findings = list(state.get("research_findings", []))
    sources = list(state.get("sources_used", []))
    messages = list(state.get("messages", []))

    try:
        sub_tasks_text = "\n".join(
            f"{i+1}. {t}" for i, t in enumerate(state.get("sub_tasks", []))
        )

        current_messages = [
            SystemMessage(content=RESEARCHER_SYSTEM_PROMPT),
            HumanMessage(content=f"""Research query: {state['query']}

Please execute these research tasks:
{sub_tasks_text}

Use the web_search tool to search for information. Call tools one at a time."""),
        ]

        max_iterations = 8
        iteration = 0

        while iteration < max_iterations:
            iteration += 1
            response = llm.invoke(current_messages)
            current_messages.append(response)

            # No tool calls — agent is done
            if not hasattr(response, 'tool_calls') or not response.tool_calls:
                logger.info(f"[Researcher] Completed in {iteration} iterations")
                if response.content:
                    findings.append(response.content)
                break

            # Execute each tool call
            for tool_call in response.tool_calls:
                tool_name = tool_call["name"]
                tool_input = tool_call["args"]
                tool_id = tool_call["id"]

                logger.info(f"[Researcher] Calling tool: {tool_name} args: {tool_input}")

                trace_events.append({
                    "type": "tool_call",
                    "agent": "researcher",
                    "content": f"Calling {tool_name} with: {tool_input}",
                    "tool_name": tool_name,
                    "tool_input": tool_input,
                    "timestamp": datetime.utcnow().isoformat(),
                })

                tool_result = _execute_tool(tool_name, tool_input)

                # Track sources
                if tool_input:
                    first_val = list(tool_input.values())[0]
                    sources.append(f"{tool_name}: {first_val}")

                trace_events.append({
                    "type": "tool_result",
                    "agent": "researcher",
                    "content": tool_result[:600] + ("..." if len(tool_result) > 600 else ""),
                    "tool_name": tool_name,
                    "tool_input": None,
                    "timestamp": datetime.utcnow().isoformat(),
                })

                current_messages.append(
                    ToolMessage(content=tool_result, tool_call_id=tool_id)
                )

        trace_events.append({
            "type": "agent_end",
            "agent": "researcher",
            "content": f"Research complete. {len(findings)} findings from {len(sources)} sources.",
            "tool_name": None,
            "tool_input": None,
            "timestamp": datetime.utcnow().isoformat(),
        })

        return {
            **state,
            "research_findings": findings,
            "sources_used": sources,
            "current_agent": "writer",
            "agent_trace": trace_events,
            "messages": messages + current_messages,
        }

    except Exception as e:
        logger.error(f"[Researcher] Failed: {e}")
        trace_events.append({
            "type": "error",
            "agent": "researcher",
            "content": f"Research failed: {str(e)}",
            "tool_name": None,
            "tool_input": None,
            "timestamp": datetime.utcnow().isoformat(),
        })
        return {
            **state,
            "research_findings": findings or ["Research failed"],
            "sources_used": sources,
            "current_agent": "writer",
            "agent_trace": trace_events,
            "error": str(e),
        }


def _execute_tool(tool_name: str, tool_input: dict) -> str:
    tool_map = {t.name: t for t in RESEARCHER_TOOLS}
    if tool_name not in tool_map:
        return f"Unknown tool: {tool_name}"
    try:
        return tool_map[tool_name].invoke(tool_input)
    except Exception as e:
        return f"Tool {tool_name} failed: {str(e)}"