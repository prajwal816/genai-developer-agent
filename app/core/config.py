"""
Application configuration management.

Loads configuration from environment variables and YAML settings file.
Uses Pydantic Settings for validation and type coercion.
"""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml
from pydantic import Field
from pydantic_settings import BaseSettings


_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
_CONFIG_PATH = _PROJECT_ROOT / "configs" / "settings.yaml"


def _load_yaml_config() -> dict[str, Any]:
    """Load YAML configuration file and return as dictionary."""
    if _CONFIG_PATH.exists():
        with open(_CONFIG_PATH, "r", encoding="utf-8") as fh:
            return yaml.safe_load(fh) or {}
    return {}


_yaml_cfg = _load_yaml_config()


class OpenAISettings(BaseSettings):
    """OpenAI provider configuration."""

    api_key: str = Field(default="", alias="OPENAI_API_KEY")
    model: str = Field(default="gpt-4o", alias="OPENAI_MODEL")
    base_url: str = Field(
        default="https://api.openai.com/v1", alias="OPENAI_BASE_URL"
    )
    max_tokens: int = Field(default=4096, alias="OPENAI_MAX_TOKENS")
    temperature: float = Field(default=0.3, alias="OPENAI_TEMPERATURE")
    timeout_seconds: int = Field(default=60, alias="OPENAI_TIMEOUT")


class LocalLLMSettings(BaseSettings):
    """Local simulation provider configuration."""

    simulated_latency_ms: int = Field(default=200)
    model_name: str = Field(default="local-simulation-v1")


class LLMSettings(BaseSettings):
    """LLM provider configuration."""

    provider: str = Field(default="local", alias="LLM_PROVIDER")
    openai: OpenAISettings = Field(default_factory=OpenAISettings)
    local: LocalLLMSettings = Field(default_factory=LocalLLMSettings)


class AgentConfig(BaseSettings):
    """Individual agent configuration."""

    enabled: bool = True
    timeout_seconds: int = 120
    max_code_length: int = 50000


class AgentsSettings(BaseSettings):
    """All agents configuration."""

    code_review: AgentConfig = Field(default_factory=AgentConfig)
    issue_classification: AgentConfig = Field(default_factory=AgentConfig)
    suggestion: AgentConfig = Field(default_factory=AgentConfig)


class ResilienceSettings(BaseSettings):
    """Retry and timeout configuration."""

    retry_max_attempts: int = Field(default=3, alias="RETRY_MAX_ATTEMPTS")
    retry_wait_seconds: float = Field(default=1.0, alias="RETRY_WAIT_SECONDS")
    retry_exponential_base: float = Field(default=2.0)
    default_timeout_seconds: int = Field(
        default=120, alias="DEFAULT_TIMEOUT_SECONDS"
    )
    circuit_breaker_failure_threshold: int = Field(default=5)
    circuit_breaker_recovery_seconds: int = Field(default=30)


class MonitoringSettings(BaseSettings):
    """Monitoring and observability configuration."""

    metrics_enabled: bool = Field(default=True, alias="METRICS_ENABLED")
    metrics_prefix: str = Field(default="genai_agent")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    log_format: str = Field(default="json")
    alert_error_threshold: int = Field(default=10)
    alert_latency_threshold_ms: int = Field(default=5000)


class Settings(BaseSettings):
    """Root application settings — single source of truth."""

    # Application
    app_name: str = Field(
        default="GenAI Developer Productivity Agent", alias="APP_NAME"
    )
    app_version: str = Field(default="1.0.0", alias="APP_VERSION")
    app_debug: bool = Field(default=False, alias="APP_DEBUG")
    app_host: str = Field(default="0.0.0.0", alias="APP_HOST")
    app_port: int = Field(default=8000, alias="APP_PORT")

    # Sub-configurations
    llm: LLMSettings = Field(default_factory=LLMSettings)
    agents: AgentsSettings = Field(default_factory=AgentsSettings)
    resilience: ResilienceSettings = Field(default_factory=ResilienceSettings)
    monitoring: MonitoringSettings = Field(default_factory=MonitoringSettings)

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Return cached application settings singleton.

    Merges environment variables (highest priority) with YAML config.
    """
    return Settings()
