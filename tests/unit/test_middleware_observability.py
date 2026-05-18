"""Testes do middleware de observabilidade — métricas Prometheus e correlation_id."""

from httpx import ASGITransport, AsyncClient

from app.main import app


class TestObservabilityMiddleware:
    """Verifica que /metrics retorna 200 e correlation_id está presente em respostas."""

    async def test_metrics_endpoint_retorna_200(self) -> None:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/metrics")
        assert response.status_code == 200
        assert "python_info" in response.text

    async def test_correlation_id_presente_no_header(self) -> None:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/health")
        assert "X-Correlation-ID" in response.headers

    async def test_correlation_id_eh_uuid_valido(self) -> None:
        from uuid import UUID

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/health")
        UUID(response.headers["X-Correlation-ID"])
