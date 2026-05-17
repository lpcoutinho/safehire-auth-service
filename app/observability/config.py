"""Configuração da stack de observabilidade baseada na variável OBSERVABILITY_STACK."""

from enum import Enum

from pydantic_settings import BaseSettings, SettingsConfigDict


class ObservabilityStack(str, Enum):
    floci = "floci"
    vps = "vps"
    aws = "aws"


class ObservabilityConfig(BaseSettings):
    stack: ObservabilityStack = ObservabilityStack.floci
    floci_endpoint: str = "http://localhost:4566"
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_region: str = "us-east-1"
    xray_daemon_address: str = "localhost:2000"
    prometheus_url: str = "http://localhost:9090"
    loki_url: str = "http://localhost:3100"
    tempo_url: str = "http://localhost:3200"
    cloudwatch_log_group: str = "/safehire/auth-service"
    trace_sampling_rate: float = 0.1
    log_level: str = "INFO"
    log_format: str = "json"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
