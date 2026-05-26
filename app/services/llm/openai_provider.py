"""
OpenAI-compatible LLM provider — concrete Strategy implementation.

Supports any OpenAI-compatible API (OpenAI, Azure, local vLLM, etc.)
with retry logic, timeout management, and structured error handling.
"""

from __future__ import annotations

import time

import httpx
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from app.core.config import get_settings
from app.core.exceptions import LLMProviderError
from app.core.logging import get_logger
from app.services.llm.base import LLMProvider, LLMRequest, LLMResponse

logger = get_logger(__name__)


class OpenAIProvider(LLMProvider):
    """
    OpenAI-compatible API provider (Strategy Pattern — concrete strategy).

    Features:
    - Async HTTP client with connection pooling
    - Exponential backoff retry on transient failures
    - Timeout management
    - Token usage tracking
    """

    def __init__(self) -> None:
        settings = get_settings()
        self._config = settings.llm.openai
        self._resilience = settings.resilience
        self._client = httpx.AsyncClient(
            base_url=self._config.base_url,
            headers={
                "Authorization": f"Bearer {self._config.api_key}",
                "Content-Type": "application/json",
            },
            timeout=httpx.Timeout(self._config.timeout_seconds),
        )

    @property
    def provider_name(self) -> str:
        return "openai"

    @property
    def model_name(self) -> str:
        return self._config.model

    @retry(
        retry=retry_if_exception_type(httpx.TransportError),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        reraise=True,
    )
    async def generate(self, request: LLMRequest) -> LLMResponse:
        """Send a completion request to the OpenAI-compatible API."""
        start_time = time.perf_counter()

        messages = []
        if request.system_prompt:
            messages.append({"role": "system", "content": request.system_prompt})
        messages.append({"role": "user", "content": request.prompt})

        payload = {
            "model": self._config.model,
            "messages": messages,
            "max_tokens": request.max_tokens,
            "temperature": request.temperature,
        }
        if request.stop_sequences:
            payload["stop"] = request.stop_sequences

        try:
            response = await self._client.post("/chat/completions", json=payload)
            response.raise_for_status()
            data = response.json()

            latency_ms = (time.perf_counter() - start_time) * 1000
            usage = data.get("usage", {})

            return LLMResponse(
                content=data["choices"][0]["message"]["content"],
                model=data.get("model", self._config.model),
                provider=self.provider_name,
                prompt_tokens=usage.get("prompt_tokens", 0),
                completion_tokens=usage.get("completion_tokens", 0),
                total_tokens=usage.get("total_tokens", 0),
                latency_ms=latency_ms,
            )

        except httpx.HTTPStatusError as exc:
            logger.error(
                "OpenAI API error",
                status_code=exc.response.status_code,
                response_body=exc.response.text[:500],
            )
            raise LLMProviderError(
                f"OpenAI API returned {exc.response.status_code}",
                provider=self.provider_name,
                details={"status_code": exc.response.status_code},
            ) from exc
        except httpx.TransportError as exc:
            logger.error("OpenAI transport error", error=str(exc))
            raise LLMProviderError(
                f"Failed to connect to OpenAI: {exc}",
                provider=self.provider_name,
            ) from exc
        except Exception as exc:
            logger.error("Unexpected OpenAI error", error=str(exc))
            raise LLMProviderError(
                f"Unexpected error: {exc}",
                provider=self.provider_name,
            ) from exc

    async def health_check(self) -> bool:
        """Check connectivity to the OpenAI API."""
        try:
            response = await self._client.get("/models")
            return response.status_code == 200
        except Exception:
            return False

    async def shutdown(self) -> None:
        """Close the HTTP client."""
        await self._client.aclose()
