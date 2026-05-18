"""Tracing distribuído — XRayTracer (floci/aws) e LocalTracer (vps) com interface única."""

from __future__ import annotations

import logging
from contextlib import contextmanager
from typing import Generator

logger = logging.getLogger(__name__)


class XRayTracer:
    """Tracing via AWS X-Ray — usado com floci (dev) ou AWS (prod)."""

    def __init__(self, daemon_address: str | None = None) -> None:
        from aws_xray_sdk.core import AWSXRayRecorder

        self._recorder = AWSXRayRecorder()
        if daemon_address:
            self._recorder.configure(daemon_address=daemon_address)

    @contextmanager
    def in_subsegment(
        self, name: str, **metadata: object
    ) -> Generator[object, None, None]:
        """Cria um subsegmento X-Ray para tracing de operações específicas.

        Uso: com tracer.in_subsegment("db.query"): await repo.buscar(...)
        """
        from aws_xray_sdk.core.models.subsegment import Subsegment

        subsegment = Subsegment(name)
        for k, v in metadata.items():
            subsegment.set_metadata(k, v)
        try:
            yield subsegment
        except Exception as e:
            subsegment.add_error_flag()
            subsegment.add_exception(e)
            raise
        finally:
            subsegment.close()


class LocalTracer:
    """Implementação local de tracing — usa logging para VPS (OpenTelemetry no futuro)."""

    def __init__(self, service_name: str = "") -> None:
        self._service = service_name
        self._logger = logging.getLogger(f"{__name__}.LocalTracer.{service_name}")

    @contextmanager
    def in_subsegment(
        self, name: str, **metadata: object
    ) -> Generator[None, None, None]:
        """Loga o início e fim de uma operação — substituto local para X-Ray.

        Uso: com tracer.in_subsegment("send_email"): ...
        """
        self._logger.debug("TRACE start %s %s", name, metadata)
        try:
            yield
        finally:
            self._logger.debug("TRACE end %s", name)
