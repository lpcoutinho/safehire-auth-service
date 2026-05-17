"""Factory que retorna a implementação correta de observability conforme a stack configurada."""

from app.config import settings


def init_observability() -> None:
    """Inicializa métricas, tracing e logging com base em settings.env.

    Uso: chamar uma vez no startup do FastAPI: `init_observability()`.
    """
    stack = settings.env
    if stack == "aws":
        _init_aws()
    elif stack == "vps":
        _init_vps()
    else:
        _init_floci()


def _init_aws() -> None:
    """Configura CloudWatch Metrics + X-Ray — stack de produção AWS."""
    pass


def _init_vps() -> None:
    """Configura Prometheus + Grafana + Loki + Tempo — stack self-hosted VPS."""
    pass


def _init_floci() -> None:
    """Configura LocalStack (Floci) simulando CloudWatch + X-Ray — stack dev local."""
    pass
