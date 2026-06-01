from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from db.database import get_db, ResearchSession
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

router = APIRouter(prefix="/api", tags=["research"])


class SessionResponse(BaseModel):
    id: str
    query: str
    status: str
    created_at: datetime
    completed_at: Optional[datetime]
    final_answer: Optional[str]

    model_config = {"from_attributes": True}


@router.get("/sessions", response_model=List[SessionResponse])
async def list_sessions(limit: int = 20, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ResearchSession)
        .order_by(desc(ResearchSession.created_at))
        .limit(limit)
    )
    sessions = result.scalars().all()
    return [
        SessionResponse(
            id=s.id,
            query=s.query,
            status=s.status,
            created_at=s.created_at,
            completed_at=s.completed_at,
            final_answer=s.final_answer,
        )
        for s in sessions
    ]


@router.get("/sessions/{session_id}", response_model=SessionResponse)
async def get_session(session_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ResearchSession).where(ResearchSession.id == session_id)
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return SessionResponse(
        id=session.id,
        query=session.query,
        status=session.status,
        created_at=session.created_at,
        completed_at=session.completed_at,
        final_answer=session.final_answer,
    )


@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ResearchSession).where(ResearchSession.id == session_id)
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    await db.delete(session)
    await db.commit()
    return {"deleted": session_id}


@router.get("/health")
async def health():
    return {"status": "ok", "service": "multi-agent-research"}
