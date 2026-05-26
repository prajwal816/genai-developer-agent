"""
Shared test fixtures for the GenAI Agent test suite.
"""

from __future__ import annotations

import asyncio
from typing import AsyncIterator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.agents.factory import AgentFactory
from app.main import app
from app.monitoring.event_bus import EventBus
from app.services.llm.base import LLMProvider
from app.services.llm.local_provider import LocalSimulationProvider


@pytest.fixture(scope="session")
def event_loop():
    """Create a session-scoped event loop."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def async_client() -> AsyncIterator[AsyncClient]:
    """Provide an async HTTP test client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture
def llm_provider() -> LLMProvider:
    """Provide a local simulation LLM provider."""
    return LocalSimulationProvider()


@pytest.fixture
def agent_factory(llm_provider: LLMProvider) -> AgentFactory:
    """Provide an AgentFactory with local LLM provider."""
    return AgentFactory(llm_provider)


@pytest.fixture(autouse=True)
def reset_event_bus():
    """Reset EventBus between tests to prevent listener leaks."""
    EventBus.reset()
    yield
    EventBus.reset()


# ── Sample test data ──

@pytest.fixture
def sample_python_code() -> str:
    return '''
def calculate_total(items):
    total = 0
    for i in range(len(items)):
        if items[i] != None:
            total = total + items[i]["price"]
    return total
'''


@pytest.fixture
def sample_review_payload() -> dict:
    return {
        "code": "def add(a, b):\\n    return a + b",
        "language": "python",
        "context": "Simple utility function",
    }


@pytest.fixture
def sample_classify_payload() -> dict:
    return {
        "title": "Application crashes on startup",
        "description": "The application fails to start with a NullPointerException in the main module.",
        "labels": ["bug"],
    }


@pytest.fixture
def sample_suggest_payload() -> dict:
    return {
        "code": "for i in range(len(lst)):\\n    print(lst[i])",
        "language": "python",
        "instruction": "Use Pythonic idioms",
    }
