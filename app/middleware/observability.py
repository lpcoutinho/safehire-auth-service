"""Middleware de observabilidade — métricas Prometheus, tracing OpenTelemetry e correlation_id em responses."""

from typing import Awaitable, Callable
from uuid import uuid4

from fastapi import FastAPI, Request, Response
from prometheus_fastapi_instrumentator import Instrumentator

ASGIHandler = Callable[[Request], Awaitable[Response]]

instrumentator = Instrumentator()


async def _add_correlation_id(request: Request, call_next: ASGIHandler) -> Response:
    """Adiciona correlation_id (UUID v4) em cada resposta para rastreamento de requisições."""
    response: Response = await call_next(request)
    response.headers["X-Correlation-ID"] = str(uuid4())
    return response


def setup_observability_middleware(app: FastAPI) -> None:
    """Configura Prometheus metrics (+ /metrics) e correlation_id em cada response.

    Uso: chamar no startup do app: setup_observability_middleware(app)
    """
    instrumentator.instrument(app).expose(app, include_in_schema=False)
    app.middleware("http")(_add_correlation_id)
