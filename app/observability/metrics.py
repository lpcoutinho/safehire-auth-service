"""Métricas — CloudWatchMetrics (floci/aws) e LocalMetrics (vps) com interface única."""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


class CloudWatchMetrics:
    """Envia métricas para CloudWatch via boto3 — usado com floci (dev) ou AWS (prod)."""

    def __init__(self, namespace: str, endpoint_url: str | None = None) -> None:
        import boto3

        self._namespace = namespace
        self._client = boto3.client(
            "cloudwatch",
            endpoint_url=endpoint_url,
            region_name="us-east-1",
            aws_access_key_id="test",
            aws_secret_access_key="test",
        )

    def put_metric(
        self,
        name: str,
        value: float,
        unit: str = "Count",
        dimensions: list[dict[str, str]] | None = None,
    ) -> None:
        """Envia uma métrica pontual para CloudWatch.

        Uso: metrics.put_metric("RequestCount", 1, dimensions=[{"Name":"Service","Value":"auth"}])
        """
        self._client.put_metric_data(
            Namespace=self._namespace,
            MetricData=[
                {
                    "MetricName": name,
                    "Value": value,
                    "Unit": unit,
                    "Dimensions": dimensions or [],
                }
            ],
        )


class LocalMetrics:
    """Implementação local de métricas — usa logging para VPS sem CloudWatch."""

    def __init__(self, service_name: str) -> None:
        self._service = service_name
        self._logger = logging.getLogger(f"{__name__}.LocalMetrics.{service_name}")

    def put_metric(
        self,
        name: str,
        value: float,
        unit: str = "Count",
        dimensions: list[dict[str, str]] | None = None,
    ) -> None:
        """Registra métrica no log — visível no Loki/Promtail se configurado.

        Uso: metrics.put_metric("cpu", 0.5, "Percent")
        """
        self._logger.info(
            "METRIC %s %s %s %s",
            name,
            value,
            unit,
            dimensions or "",
        )
