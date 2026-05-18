"""Logger estruturado em JSON com timestamp, level, service e trace_id — via python-json-logger."""

from __future__ import annotations

import logging
import sys

from pythonjsonlogger import jsonlogger


def setup_logging(service_name: str, log_level: str = "INFO") -> logging.Logger:
    """Configura logger estruturado JSON com campos padronizados.

    Uso: logger = setup_logging("auth-service", "DEBUG")
         logger.info("mensagem", extra={"trace_id": "abc"})
    """
    level = getattr(logging, log_level.upper(), logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    formatter = jsonlogger.JsonFormatter(  # type: ignore[no-untyped-call]
        fmt="%(asctime)s %(levelname)s %(name)s %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )
    handler.setFormatter(formatter)

    logger = logging.getLogger(service_name)
    logger.setLevel(level)
    logger.handlers.clear()
    logger.addHandler(handler)
    logger.propagate = False

    return logger
