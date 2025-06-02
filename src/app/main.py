from fastapi import FastAPI
from contextlib import asynccontextmanager
from .config.config import get_settings
from .routes import health, admin_router
from fastapi.middleware.cors import CORSMiddleware

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    from .db.db_client import get_client

    await get_client().admin.command("ping")  # fail fast
    yield

    get_client().close()


app = FastAPI(title="ClassConnect Template", version="1.0.0", lifespan=lifespan)

app.include_router(health.router)
app.include_router(admin_router.router, prefix="/admin", tags=["admin"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to your needs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
