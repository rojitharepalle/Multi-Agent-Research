from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from agents.pipeline import run_research_pipeline
from db.database import AsyncSessionLocal, ResearchSession
from core.logging import logger
from datetime import datetime
import json
import uuid

router = APIRouter()


class ConnectionManager:
    def __init__(self):
        self.active: dict[str, WebSocket] = {}

    async def connect(self, session_id: str, ws: WebSocket):
        await ws.accept()
        self.active[session_id] = ws
        logger.info(f"[WS] Connected: {session_id}")

    def disconnect(self, session_id: str):
        self.active.pop(session_id, None)
        logger.info(f"[WS] Disconnected: {session_id}")

    async def send(self, session_id: str, data: dict):
        ws = self.active.get(session_id)
        if ws:
            try:
                await ws.send_text(json.dumps(data))
            except Exception as e:
                logger.warning(f"[WS] Send failed for {session_id}: {e}")


manager = ConnectionManager()


@router.websocket("/ws/research/{session_id}")
async def research_websocket(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for real-time agent streaming.

    Protocol:
    - Client sends : {"query": "research question"}
    - Server streams: {"type": "session_start|agent_event|final|error", "data": {...}}
    """
    await manager.connect(session_id, websocket)

    try:
        # Wait for query from client
        raw = await websocket.receive_text()
        payload = json.loads(raw)
        query = payload.get("query", "").strip()

        if not query:
            await manager.send(session_id, {
                "type": "error",
                "data": {"message": "Query cannot be empty"}
            })
            return

        # Acknowledge start
        await manager.send(session_id, {
            "type": "session_start",
            "data": {"session_id": session_id, "query": query}
        })

        # Stream callback — called for every agent event
        async def stream_event(event: dict):
            await manager.send(session_id, {
                "type": "agent_event",
                "data": event,
            })

        # Run the full pipeline
        final_state = await run_research_pipeline(
            query=query,
            session_id=session_id,
            on_event=stream_event,
        )

        # Save session to database
        await _save_session(session_id, query, final_state)

        # Send final result
        await manager.send(session_id, {
            "type": "final",
            "data": {
                "session_id": session_id,
                "query": query,
                "final_answer": final_state.get("final_answer", ""),
                "sources_used": final_state.get("sources_used", []),
                "status": final_state.get("status", "completed"),
            }
        })

    except WebSocketDisconnect:
        logger.info(f"[WS] Client disconnected: {session_id}")
    except Exception as e:
        logger.error(f"[WS] Error for {session_id}: {e}")
        await manager.send(session_id, {
            "type": "error",
            "data": {"message": str(e)}
        })
    finally:
        manager.disconnect(session_id)


async def _save_session(session_id: str, query: str, state: dict):
    try:
        async with AsyncSessionLocal() as db:
            session = ResearchSession(
                id=session_id,
                query=query,
                status=state.get("status", "completed"),
                completed_at=datetime.utcnow(),
                final_answer=state.get("final_answer"),
                agent_trace=state.get("agent_trace", []),
            )
            db.add(session)
            await db.commit()
            logger.info(f"[WS] Session saved: {session_id}")
    except Exception as e:
        logger.error(f"[WS] Failed to save session: {e}")
