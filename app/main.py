"""Entry point FastAPI — inicializa app, inclui routers e endpoints de health check."""

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.config import settings
from app.middleware.observability import setup_observability_middleware
from app.routes import auth, usuarios

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    debug=settings.debug,
)

setup_observability_middleware(app)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(usuarios.router, prefix="/usuarios", tags=["usuarios"])


@app.get("/health")
async def health() -> JSONResponse:
    """Health check usado por load balancers e orquestradores (ECS, Docker Compose).

    Uso: `curl localhost:8001/health` → {"status": "ok", "service": "SafeHire Auth Service"}
    """
    return JSONResponse(content={"status": "ok", "service": settings.app_name})
