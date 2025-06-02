from fastapi import FastAPI
from contextlib import asynccontextmanager
from src.app.config.config import get_settings
from src.app.routes import health, admin_router
from fastapi.middleware.cors import CORSMiddleware

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    from src.app.db.db_client import get_client

    await get_client().admin.command("ping")
    print(f"🚀 Servidor escuchando en http://{settings.host}:{settings.port}")
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
