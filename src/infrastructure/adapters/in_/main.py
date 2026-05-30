from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.infrastructure.adapters.in_.cursos_router import router as cursos_router
from src.infrastructure.adapters.in_.recursos_router import router as recursos_router
from src.infrastructure.config.settings import settings
from src.infrastructure.db.database import engine
from src.infrastructure.db.models.cursos_models import Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(title="SWARD — Cursos y Recursos", version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)
app.include_router(cursos_router)
app.include_router(recursos_router)


@app.get("/health")
async def health():
    return {"status": "ok", "service": settings.service_name}
