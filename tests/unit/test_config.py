"""Testes para app.config — carregamento de env vars, defaults e observability stack."""

import os
from unittest.mock import patch

from app.config import Settings, settings


class TestConfigDefaults:
    """Valores padrão do Settings quando nenhuma env var é definida."""

    def test_secret_key_tem_valor_padrao(self):
        assert settings.secret_key == "change-me-to-a-long-random-secret-key"

    def test_algorithm_padrao_e_hs256(self):
        assert settings.algorithm == "HS256"

    def test_access_token_expira_em_30_minutos(self):
        assert settings.access_token_expire_minutes == 30

    def test_refresh_token_expira_em_7_dias(self):
        assert settings.refresh_token_expire_days == 7

    def test_debug_e_true_por_padrao(self):
        assert settings.debug is True

    def test_env_padrao_e_development(self):
        assert settings.env == "development"

    def test_host_padrao_e_0_0_0_0(self):
        assert settings.host == "0.0.0.0"

    def test_port_padrao_e_8001(self):
        assert settings.port == 8001

    def test_observability_stack_padrao_e_floci(self):
        assert settings.observability_stack == "floci"

    def test_log_level_padrao_e_info(self):
        assert settings.log_level == "INFO"

    def test_allowed_origins_padrao(self):
        assert "localhost:3000" in settings.allowed_origins

    def test_floci_endpoint_padrao(self):
        assert settings.floci_endpoint == "http://floci:4566"


class TestConfigFromEnv:
    """Settings lê de variáveis de ambiente quando definidas."""

    def test_env_var_sobrescreve_database_url(self):
        with patch.dict(os.environ, {"DATABASE_URL": "sqlite:///test.db"}, clear=False):
            s = Settings()
            assert s.database_url == "sqlite:///test.db"

    def test_env_var_sobrescreve_secret_key(self):
        with patch.dict(os.environ, {"SECRET_KEY": "custom-secret"}, clear=False):
            s = Settings()
            assert s.secret_key == "custom-secret"

    def test_env_var_sobrescreve_observability_stack(self):
        with patch.dict(os.environ, {"OBSERVABILITY_STACK": "aws"}, clear=False):
            s = Settings()
            assert s.observability_stack == "aws"

    def test_env_var_sobrescreve_log_level(self):
        with patch.dict(os.environ, {"LOG_LEVEL": "DEBUG"}, clear=False):
            s = Settings()
            assert s.log_level == "DEBUG"

    def test_env_var_sobrescreve_debug(self):
        with patch.dict(os.environ, {"DEBUG": "false"}, clear=False):
            s = Settings()
            assert s.debug is False
