import asyncio
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .config import get_settings
from .database import Base, engine
from .routers import machines, telemetry, auth, token_usage
from .tasks import cleanup_loop

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created")

    settings = get_settings()
    task = asyncio.create_task(
        cleanup_loop(settings.cleanup_interval_hours, settings.retention_days)
    )
    yield
    task.cancel()


app = FastAPI(title="Nado Monitor", version="1.0.0", lifespan=lifespan)

settings = get_settings()
origins = settings.cors_origins.split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=("*" not in origins),
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(telemetry.router, prefix="/api")
app.include_router(machines.router, prefix="/api")
app.include_router(token_usage.router, prefix="/api")


@app.get("/api/health")
def health():
    return {"status": "ok"}


# Serve built frontend in production
# In dev: server/app/main.py → ../../.. = project root
# In deploy: app/main.py → ../.. = wwwroot (deploy root)
_app_dir = Path(__file__).parent.parent
frontend_dist = _app_dir.parent / "dashboard" / "dist"
if not frontend_dist.exists():
    frontend_dist = _app_dir / "dashboard" / "dist"
if frontend_dist.exists():
    app.mount(
        "/assets",
        StaticFiles(directory=str(frontend_dist / "assets")),
        name="assets",
    )

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        file_path = (frontend_dist / full_path).resolve()
        dist_resolved = frontend_dist.resolve()
        if (
            str(file_path).startswith(str(dist_resolved))
            and file_path.exists()
            and file_path.is_file()
        ):
            return FileResponse(str(file_path))
        return FileResponse(str(frontend_dist / "index.html"))
