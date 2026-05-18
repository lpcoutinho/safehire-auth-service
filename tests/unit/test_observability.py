"""Testes da camada de observabilidade — factory, métricas, tracing e logging estruturado."""

import io
import logging
from unittest.mock import MagicMock, patch

from app.observability.config import ObservabilityConfig, ObservabilityStack


class TestObservabilityConfig:
    """Valida que ObservabilityConfig carrega defaults e aceita override por env."""

    def test_stack_default_e_floci(self) -> None:
        config = ObservabilityConfig()
        assert config.stack == ObservabilityStack.floci

    def test_stack_override_por_env(self) -> None:
        config = ObservabilityConfig(stack=ObservabilityStack.vps)
        assert config.stack == ObservabilityStack.vps


class TestCloudWatchMetrics:
    """Testa CloudWatchMetrics com boto3 mockado."""

    def test_put_metric_envia_dados(self) -> None:
        mock_client = MagicMock()
        with patch("boto3.client", return_value=mock_client):
            from app.observability.metrics import CloudWatchMetrics

            metrics = CloudWatchMetrics(namespace="SafeHire/test", endpoint_url=None)
            metrics.put_metric(name="TestMetric", value=1.0, unit="Count")
        mock_client.put_metric_data.assert_called_once_with(
            Namespace="SafeHire/test",
            MetricData=[
                {
                    "MetricName": "TestMetric",
                    "Value": 1.0,
                    "Unit": "Count",
                    "Dimensions": [],
                }
            ],
        )

    def test_put_metric_com_dimensions(self) -> None:
        mock_client = MagicMock()
        with patch("boto3.client", return_value=mock_client):
            from app.observability.metrics import CloudWatchMetrics

            metrics = CloudWatchMetrics(namespace="SafeHire/test", endpoint_url=None)
            metrics.put_metric(
                name="TestMetric",
                value=42.0,
                unit="Count",
                dimensions=[{"Name": "Service", "Value": "auth"}],
            )
        call_kwargs = mock_client.put_metric_data.call_args[1]
        assert call_kwargs["MetricData"][0]["Dimensions"] == [
            {"Name": "Service", "Value": "auth"}
        ]


class TestLocalMetrics:
    """Testa LocalMetrics — implementação dummy que usa logging."""

    def test_put_metric_loga_sem_erro(self) -> None:
        from app.observability.metrics import LocalMetrics

        metrics = LocalMetrics(service_name="test")
        metrics.put_metric(name="cpu", value=0.5, unit="Percent")


class TestLogging:
    """Testa que o logger estruturado produz JSON e não quebra."""

    def test_logger_escreve_json_no_stdout(self) -> None:
        from app.observability.logging import setup_logging

        logger = setup_logging(service_name="test-service", log_level="INFO")
        assert logger.handlers
        handler = logger.handlers[0]
        assert isinstance(handler, logging.StreamHandler)
        old_stream = handler.stream
        handler.stream = io.StringIO()
        try:
            logger.info("hello observability")
            output = handler.stream.getvalue()
        finally:
            handler.stream = old_stream
        assert '"message": "hello observability"' in output
        assert '"levelname": "INFO"' in output

    def test_setup_nao_quebra_com_level_invalido(self) -> None:
        from app.observability.logging import setup_logging

        logger = setup_logging(service_name="test", log_level="DESCONHECIDO")
        assert logger is not None
        logger.info("fallback funciona")


class TestFactory:
    """Testa que init_observability instancia os componentes corretos por stack."""

    @patch("app.observability.metrics.CloudWatchMetrics")
    @patch("app.observability.tracing.XRayTracer")
    @patch("app.observability.factory.setup_logging")
    def test_init_floci_cria_cloudwatch(
        self, mock_logging: MagicMock, mock_tracer: MagicMock, mock_metrics: MagicMock
    ) -> None:
        from app.observability.factory import init_observability

        init_observability()
        mock_metrics.assert_called_once()

    @patch("app.observability.metrics.LocalMetrics")
    @patch("app.observability.tracing.LocalTracer")
    @patch("app.observability.factory.setup_logging")
    def test_init_vps_cria_local(
        self, mock_logging: MagicMock, mock_tracer: MagicMock, mock_metrics: MagicMock
    ) -> None:
        from app.config import settings

        original = settings.observability_stack
        settings.observability_stack = "vps"
        try:
            from app.observability.factory import init_observability

            init_observability()
            mock_metrics.assert_called_once()
        finally:
            settings.observability_stack = original
