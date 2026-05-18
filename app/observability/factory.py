"""Factory — inicializa métricas, tracing e logging conforme a stack configurada."""

from __future__ import annotations

from app.config import settings
from app.observability import metrics, tracing
from app.observability.logging import setup_logging

_metrics: metrics.CloudWatchMetrics | metrics.LocalMetrics | None = None
_tracer: tracing.XRayTracer | tracing.LocalTracer | None = None


def init_observability() -> None:
    """Inicializa métricas, tracing e logging com base em settings.observability_stack.

    Uso: chamar no startup do FastAPI: init_observability()
    """
    global _metrics, _tracer

    stack = settings.observability_stack
    setup_logging(service_name=settings.app_name, log_level=settings.log_level)

    if stack in ("floci", "aws"):
        endpoint = settings.floci_endpoint if stack == "floci" else None
        _metrics = metrics.CloudWatchMetrics(
            namespace=f"SafeHire/{settings.app_name}",
            endpoint_url=endpoint,
        )
        _tracer = tracing.XRayTracer(
            daemon_address=settings.xray_daemon_address,
        )
    else:
        _metrics = metrics.LocalMetrics(service_name=settings.app_name)
        _tracer = tracing.LocalTracer(service_name=settings.app_name)
