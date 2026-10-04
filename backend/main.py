from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from config import settings
from api.router import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    Path(settings.output_dir).mkdir(exist_ok=True)
    yield


app = FastAPI(title="Video Voice Translator", version="2.0.0", lifespan=lifespan)

# CORS — Allow the Vite dev-server (5173) to access FastAPI (8000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")

# Production: Deploying the built React application from frontend/dist
_dist = Path(__file__).parent.parent / "frontend" / "dist"
if _dist.exists():
    app.mount("/", StaticFiles(directory=str(_dist), html=True), name="ui")
