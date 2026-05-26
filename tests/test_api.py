"""
API integration tests — tests all REST endpoints end-to-end.
"""

from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestHealthEndpoint:
    """Tests for GET /health."""

    async def test_health_returns_200(self, async_client: AsyncClient):
        response = await async_client.get("/health")
        assert response.status_code == 200

    async def test_health_response_structure(self, async_client: AsyncClient):
        response = await async_client.get("/health")
        data = response.json()
        assert "status" in data
        assert "version" in data
        assert "llm_provider" in data
        assert "agents_loaded" in data
        assert data["status"] in ("healthy", "degraded")

    async def test_health_shows_agents(self, async_client: AsyncClient):
        response = await async_client.get("/health")
        data = response.json()
        assert "code_review" in data["agents_loaded"]
        assert "issue_classification" in data["agents_loaded"]
        assert "suggestion" in data["agents_loaded"]


@pytest.mark.asyncio
class TestMetricsEndpoint:
    """Tests for GET /metrics."""

    async def test_metrics_returns_200(self, async_client: AsyncClient):
        response = await async_client.get("/metrics")
        assert response.status_code == 200

    async def test_metrics_response_structure(self, async_client: AsyncClient):
        response = await async_client.get("/metrics")
        data = response.json()
        assert "total_requests" in data
        assert "average_latency_ms" in data
        assert "error_count" in data


@pytest.mark.asyncio
class TestReviewEndpoint:
    """Tests for POST /review."""

    async def test_review_returns_200(self, async_client: AsyncClient, sample_review_payload):
        response = await async_client.post("/review", json=sample_review_payload)
        assert response.status_code == 200

    async def test_review_response_structure(self, async_client: AsyncClient, sample_review_payload):
        response = await async_client.post("/review", json=sample_review_payload)
        data = response.json()
        assert "issues" in data
        assert "summary" in data
        assert "score" in data
        assert "suggestions" in data
        assert "language" in data
        assert "execution_time_ms" in data

    async def test_review_score_range(self, async_client: AsyncClient, sample_review_payload):
        response = await async_client.post("/review", json=sample_review_payload)
        data = response.json()
        assert 0.0 <= data["score"] <= 10.0

    async def test_review_detects_issues(self, async_client: AsyncClient):
        payload = {
            "code": "import os\\nresult = eval(user_input)\\nexcept:\\n    pass",
            "language": "python",
        }
        response = await async_client.post("/review", json=payload)
        data = response.json()
        assert len(data["issues"]) > 0

    async def test_review_validation_error(self, async_client: AsyncClient):
        response = await async_client.post("/review", json={"language": "python"})
        assert response.status_code == 422

    async def test_review_empty_code_rejected(self, async_client: AsyncClient):
        response = await async_client.post("/review", json={"code": "", "language": "python"})
        assert response.status_code == 422


@pytest.mark.asyncio
class TestClassifyEndpoint:
    """Tests for POST /classify."""

    async def test_classify_returns_200(self, async_client: AsyncClient, sample_classify_payload):
        response = await async_client.post("/classify", json=sample_classify_payload)
        assert response.status_code == 200

    async def test_classify_response_structure(self, async_client: AsyncClient, sample_classify_payload):
        response = await async_client.post("/classify", json=sample_classify_payload)
        data = response.json()
        assert "category" in data
        assert "priority" in data
        assert "confidence" in data
        assert "reasoning" in data

    async def test_classify_confidence_range(self, async_client: AsyncClient, sample_classify_payload):
        response = await async_client.post("/classify", json=sample_classify_payload)
        data = response.json()
        assert 0.0 <= data["confidence"] <= 1.0

    async def test_classify_bug_detection(self, async_client: AsyncClient):
        payload = {
            "title": "Application crashes with NullPointerException",
            "description": "The app crashes when clicking the submit button. Error logs show NPE.",
        }
        response = await async_client.post("/classify", json=payload)
        data = response.json()
        assert data["category"] == "bug"

    async def test_classify_validation_error(self, async_client: AsyncClient):
        response = await async_client.post("/classify", json={"title": "test"})
        assert response.status_code == 422


@pytest.mark.asyncio
class TestSuggestEndpoint:
    """Tests for POST /suggest."""

    async def test_suggest_returns_200(self, async_client: AsyncClient, sample_suggest_payload):
        response = await async_client.post("/suggest", json=sample_suggest_payload)
        assert response.status_code == 200

    async def test_suggest_response_structure(self, async_client: AsyncClient, sample_suggest_payload):
        response = await async_client.post("/suggest", json=sample_suggest_payload)
        data = response.json()
        assert "original_code" in data
        assert "suggested_code" in data
        assert "explanation" in data
        assert "improvements" in data

    async def test_suggest_provides_improvements(self, async_client: AsyncClient, sample_suggest_payload):
        response = await async_client.post("/suggest", json=sample_suggest_payload)
        data = response.json()
        assert len(data["improvements"]) > 0

    async def test_suggest_validation_error(self, async_client: AsyncClient):
        response = await async_client.post("/suggest", json={"language": "python"})
        assert response.status_code == 422


@pytest.mark.asyncio
class TestAPIv1Prefix:
    """Tests for /api/v1 prefix routing."""

    async def test_v1_health(self, async_client: AsyncClient):
        response = await async_client.get("/api/v1/health")
        assert response.status_code == 200

    async def test_v1_review(self, async_client: AsyncClient, sample_review_payload):
        response = await async_client.post("/api/v1/review", json=sample_review_payload)
        assert response.status_code == 200
