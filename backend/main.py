import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from dotenv import load_dotenv
from starlette.middleware.base import BaseHTTPMiddleware

# Load environment variables from backend/.env (preferred),
# fallback to process env and optionally .env.example for local dev.
# Resolve important directories
BASE_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, os.pardir))

# .env loading (prefer backend/.env; fallback to process env and then .env.example)
env_path = os.path.join(BASE_DIR, ".env")
example_env_path = os.path.join(BASE_DIR, ".env.example")
if os.path.exists(env_path):
    load_dotenv(env_path)
else:
    load_dotenv()
    if os.path.exists(example_env_path):
        load_dotenv(example_env_path)

app = FastAPI(title="DesignMate API")
# Add cache control for latest image to avoid stale preview
class NoStoreLatestMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        try:
            path = request.url.path
            if path.endswith("/static/outputs/latest.png") or path.endswith("static/outputs/latest.png"):
                response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
                response.headers["Pragma"] = "no-cache"
                response.headers["Expires"] = "0"
        except Exception:
            pass
        return response

app.add_middleware(NoStoreLatestMiddleware)

# Frontend dist path resolution with environment override
# FRONTEND_DIST can be absolute or relative to project root
frontend_dist_env = os.getenv("FRONTEND_DIST", os.path.join(PROJECT_ROOT, "frontend", "dist"))
frontend_dist_path = (
    frontend_dist_env
    if os.path.isabs(frontend_dist_env)
    else os.path.abspath(os.path.join(PROJECT_ROOT, frontend_dist_env))
)

# Mount frontend assets under /assets if available
assets_path = os.path.join(frontend_dist_path, "assets")
if os.path.isdir(assets_path):
    app.mount("/assets", StaticFiles(directory=assets_path), name="assets")
else:
    # Avoid crashing during development before the first frontend build
    # The root route will still guard for index.html existence
    pass

# Serve backend static files (generated outputs) from backend/static
backend_static_dir = os.path.join(BASE_DIR, "static")
if os.path.isdir(backend_static_dir):
    app.mount("/static", StaticFiles(directory=backend_static_dir), name="static")

@app.get("/")
async def serve_root():
    index_path = os.path.join(frontend_dist_path, "index.html")
    if not os.path.isfile(index_path):
        # Return 404 instead of crashing the app; instruct to build the frontend
        raise HTTPException(status_code=404, detail=f"Frontend not built. Missing '{index_path}'. Run 'npm run build' in the frontend directory.")
    return FileResponse(index_path)


origins_env = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:8080,http://localhost:3000,http://localhost:5173,http://localhost:8000"
)
allow_all = os.getenv("CORS_ALLOW_ALL", "false").lower() in {"1", "true", "yes"}
origins = [o.strip() for o in origins_env.split(",") if o.strip()]

# Ensure backend preview origin is allowed by default
if "http://localhost:8000" not in origins:
    origins.append("http://localhost:8000")

cors_kwargs = {
    "allow_methods": ["*"],
    "allow_headers": ["*"],
}
if allow_all or origins == ["*"]:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,  # wildcard origins cannot be used with credentials
        **cors_kwargs,
    )
else:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        **cors_kwargs,
    )

# SPA fallback: serve frontend index.html for non-API GET routes like /workspace
@app.get("/{full_path:path}")
async def spa_fallback(full_path: str):
    # Don't intercept API/static routes
    blocked_prefixes = (
        "upload/", "generate/", "recommend/",
        "assistant/", "ai-assistant/", "static/", "assets/", "health"
    )
    if any(full_path.startswith(p) for p in blocked_prefixes):
        raise HTTPException(status_code=404, detail="Not Found")
    index_path = os.path.join(frontend_dist_path, "index.html")
    if not os.path.isfile(index_path):
        raise HTTPException(status_code=404, detail="Frontend not built. Run 'npm run build' in frontend.")
    return FileResponse(index_path)

from routes import generate, recommend, upload as upload_router, assistant, auth
from utils.logger import get_logger
from models.model_loader import ModelLoader

logger = get_logger()

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(upload_router.router, prefix="/upload", tags=["upload"])
app.include_router(generate.router, prefix="/generate", tags=["generate"])
app.include_router(recommend.router, prefix="/recommend", tags=["recommend"])
# History router removed per requirement
app.include_router(assistant.router, prefix="/assistant", tags=["assistant"])
app.include_router(assistant.router, prefix="/ai-assistant", tags=["ai-assistant"])

@app.on_event("startup")
async def startup_event():
    logger.info("Starting up: loading model into memory...")
    ModelLoader.instance().load()
    logger.info("Model loaded successfully.")

@app.get("/health")
async def health():
    return {"status": "ok"}
