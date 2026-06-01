from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, String, Text, DateTime, Float, JSON
from datetime import datetime
import uuid
from core.config import settings


engine = create_async_engine(settings.database_url, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


class ResearchSession(Base):
    __tablename__ = "research_sessions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    query = Column(Text, nullable=False)
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    final_answer = Column(Text, nullable=True)
    agent_trace = Column(JSON, default=list)
    metadata_ = Column("metadata", JSON, default=dict)


class ResearchDocument(Base):
    __tablename__ = "research_documents"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, nullable=False)
    source = Column(String)
    content = Column(Text)
    doc_type = Column(String)
    relevance_score = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class KnowledgeBase(Base):
    __tablename__ = "knowledge_base"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    topic = Column(String, nullable=False)
    title = Column(String, nullable=False)
    summary = Column(Text)
    source_url = Column(String, nullable=True)
    tags = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await seed_knowledge_base()


async def seed_knowledge_base():
    async with AsyncSessionLocal() as session:
        from sqlalchemy import select
        result = await session.execute(select(KnowledgeBase).limit(1))
        if result.scalar():
            return

        demo_entries = [
            KnowledgeBase(
                topic="AI", title="Large Language Models Overview",
                summary="LLMs are neural networks trained on vast text corpora. GPT-4, Claude, and Gemini are leading examples.",
                tags=["AI", "NLP", "deep learning"]
            ),
            KnowledgeBase(
                topic="AI", title="Retrieval Augmented Generation",
                summary="RAG combines retrieval systems with generation models to ground outputs in factual documents.",
                tags=["RAG", "AI", "retrieval"]
            ),
            KnowledgeBase(
                topic="Finance", title="S&P 500 Historical Returns",
                summary="The S&P 500 has averaged ~10% annual returns over long periods.",
                tags=["finance", "stocks", "investing"]
            ),
            KnowledgeBase(
                topic="Science", title="CRISPR Gene Editing",
                summary="CRISPR-Cas9 allows precise genome editing. Nobel Prize awarded in 2020.",
                tags=["science", "biology", "genetics"]
            ),
            KnowledgeBase(
                topic="Technology", title="Quantum Computing Basics",
                summary="Quantum computers use qubits and superposition. IBM and Google are leading hardware providers.",
                tags=["quantum", "computing", "technology"]
            ),
        ]
        session.add_all(demo_entries)
        await session.commit()


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
