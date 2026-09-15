import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import Base, SessionLocal, engine
from app.routers import commodities, epc, export
from app.scheduler import start_scheduler
from app.seed import seed_demo_history
from app.services.epc import ensure_defaults_seeded

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_demo_history(db)
        ensure_defaults_seeded(db)
    finally:
        db.close()
    scheduler = start_scheduler()
    yield
    scheduler.shutdown()


app = FastAPI(title="Solar EPC Commodity Intelligence Dashboard", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(commodities.router)
app.include_router(epc.router)
app.include_router(export.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}
