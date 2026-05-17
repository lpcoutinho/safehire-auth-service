"""Serviço JWT — criação e verificação de access/refresh tokens com python-jose."""

from datetime import datetime, timedelta, timezone
from uuid import UUID

from jose import JWTError, jwt

from app.config import settings
from app.models.auth import TokenPayload


class JWTService:
    """Serviço de tokens JWT — encapsula python-jose para criar e verificar tokens assinados.

    Uso: `JWTService().criar_access_token(usuario_id)`
    """

    def __init__(self) -> None:
        self._secret = settings.secret_key
        self._algorithm = settings.algorithm
        self._access_expire = settings.access_token_expire_minutes
        self._refresh_expire = settings.refresh_token_expire_days

    def criar_access_token(self, usuario_id: UUID) -> str:
        """Cria JWT access token com expiração curta (configurada em minutos).

        Uso: `token = jwt_service.criar_access_token(uuid4())`
        """
        exp = datetime.now(timezone.utc) + timedelta(minutes=self._access_expire)
        payload = TokenPayload(sub=usuario_id, exp=int(exp.timestamp()), tipo="access")
        token: str = jwt.encode(
            payload.model_dump(mode="json"), self._secret, algorithm=self._algorithm
        )
        return token

    def criar_refresh_token(self, usuario_id: UUID) -> str:
        """Cria JWT refresh token com expiração longa (configurada em dias).

        Uso: `token = jwt_service.criar_refresh_token(uuid4())`
        """
        exp = datetime.now(timezone.utc) + timedelta(days=self._refresh_expire)
        payload = TokenPayload(sub=usuario_id, exp=int(exp.timestamp()), tipo="refresh")
        token: str = jwt.encode(
            payload.model_dump(mode="json"), self._secret, algorithm=self._algorithm
        )
        return token

    def verificar_token(self, token: str) -> TokenPayload:
        """Decodifica e valida um JWT — retorna payload ou levanta ValueError se inválido.

        Uso: `payload = jwt_service.verificar_token("eyJ...")`
        """
        try:
            data = jwt.decode(token, self._secret, algorithms=[self._algorithm])
            return TokenPayload(**data)
        except JWTError as e:
            raise ValueError(f"Token inválido: {e}") from e
