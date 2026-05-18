"""Testes de integração do entry point — health check, documentação e métricas."""

from httpx import ASGITransport, AsyncClient

from app.main import app


class TestHealthEndpoint:
    """Verifica que /health retorna status 200 com informações do serviço."""

    async def test_health_retorna_200(self) -> None:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/health")
        assert response.status_code == 200

    async def test_health_contem_status_e_service(self) -> None:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/health")
        body = response.json()
        assert body["status"] == "ok"
        assert "service" in body
        assert "SafeHire" in body["service"]


class TestDocsEndpoint:
    """Verifica que a documentação Swagger está disponível."""

    async def test_docs_retorna_200(self) -> None:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/docs")
        assert response.status_code == 200
        assert "swagger" in response.text.lower()


class TestMetricsEndpoint:
    """Verifica que o endpoint Prometheus /metrics está exposto."""

    async def test_metrics_retorna_200(self) -> None:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/metrics")
        assert response.status_code == 200
        assert "python_info" in response.text
