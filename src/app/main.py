from fastapi import FastAPI
from contextlib import asynccontextmanager
from .config.config import get_settings
from .routes import health, assignment

settings = get_settings()
app = FastAPI(title="ClassConnect Template", version="1.0.0")

app.include_router(health.router)
app.include_router(assignment.router)

# Middleware for CORS
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to your needs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    from .db.client import get_client
    await get_client().admin.command("ping")  # fail fast
    yield

    get_client().close()
