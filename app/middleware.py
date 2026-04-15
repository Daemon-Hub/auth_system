import logging
import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request

logger = logging.getLogger(__name__)

class AuditAndPerformanceMiddleware(BaseHTTPMiddleware):
    """
    Инфраструктурный аудит, Request ID и замер времени (APM)
    """
    async def dispatch(self, request: Request, call_next):
        # Генерация Request-ID (если его прислал балансировщик, берем его)
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        
        start_time = time.perf_counter()

        response = await call_next(request)

        process_time = time.perf_counter() - start_time

        # Инъекция служебных заголовков в ответ
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = f"{process_time:.4f}"

        # Логирование медленных запросов (порог: 500мс)
        if process_time > 0.5:
            logger.warning(
                f"Slow API Request | ID: {request_id} | "
                f"Path: {request.url.path} | Method: {request.method} | "
                f"Time: {process_time:.4f}s"
            )

        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Усиление безопасности (Security Headers)
    """
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Базовая защита от MIME-типов (предотвращает sniffering)
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # Защита от Clickjacking
        response.headers["X-Frame-Options"] = "DENY"
        
        # Принудительное использование HTTPS (только для продакшена)
        # response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        return response
