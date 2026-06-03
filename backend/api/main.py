from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from api.routes import router as rest_router
from api.websocket import router as ws_router
from db.database import init_db
from core.config import settings
from core.logging import setup_logging, logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    logger.info("Starting Multi-Agent Research API")
    await init_db()
    logger.info("Database initialized")
    yield
    logger.info("Shutting down")


app = FastAPI(
    title="Multi-Agent Research System",
    description="A production-grade multi-agent AI research system",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(rest_router)
app.include_router(ws_router)


@app.get("/")
async def root():
    return {
        "service": "Multi-Agent Research System",
        "version": "1.0.0",
        "docs": "/docs",
        "websocket": "ws://localhost:8000/ws/research/{session_id}",
    }
