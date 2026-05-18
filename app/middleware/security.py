"""Middleware de segurança — headers de proteção contra ataques XSS, clickjacking, MIME sniffing."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Adiciona headers de segurança em toda resposta: HSTS, X-Frame-Options, X-Content-Type-Options, CSP.

    Uso: `app.add_middleware(SecurityHeadersMiddleware)`
    """

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains"
        )
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        return response


def setup_security_middleware(app: FastAPI) -> None:
    """Registra o middleware de security headers no app.

    Uso: chamar no startup: setup_security_middleware(app)
    """
    app.add_middleware(SecurityHeadersMiddleware)
