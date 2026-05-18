"""Entry point do Auth Service FastAPI — orquestra configuração, rotas, middleware e observabilidade."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.middleware.observability import setup_observability_middleware
from app.observability.factory import init_observability
from app.routes import auth, usuarios

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    debug=settings.debug,
)

origins = [o.strip() for o in settings.allowed_origins.split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_observability()
setup_observability_middleware(app)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(usuarios.router, prefix="/usuarios", tags=["usuarios"])


@app.get("/health")
async def health() -> dict[str, str]:
    """Health check usado por load balancers e orquestradores (ECS, Docker Compose).

    Uso: `curl localhost:8001/health` → {"status": "ok", "service": "SafeHire Auth Service"}
    """
    return {"status": "ok", "service": settings.app_name}
