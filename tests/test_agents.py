"""
Unit tests for AI agents.
"""

from __future__ import annotations

import pytest

from app.agents.code_review_agent import CodeReviewAgent
from app.agents.factory import AgentFactory
from app.agents.issue_classification_agent import IssueClassificationAgent
from app.agents.suggestion_agent import SuggestionAgent
from app.core.exceptions import AgentExecutionError, AgentNotFoundError
from app.services.llm.base import LLMProvider


@pytest.mark.asyncio
class TestCodeReviewAgent:
    """Tests for the CodeReviewAgent."""

    async def test_execute_returns_result(self, llm_provider: LLMProvider):
        agent = CodeReviewAgent(llm_provider)
        result = await agent.execute({"code": "def foo(): pass", "language": "python"})
        assert result.success is True
        assert result.agent_name == "code_review_agent"
        assert result.execution_time_ms > 0

    async def test_result_has_issues(self, llm_provider: LLMProvider):
        agent = CodeReviewAgent(llm_provider)
        result = await agent.execute({
            "code": "result = eval(input())\nexcept:\n    pass",
            "language": "python",
        })
        assert "issues" in result.result
        assert len(result.result["issues"]) > 0

    async def test_result_has_score(self, llm_provider: LLMProvider):
        agent = CodeReviewAgent(llm_provider)
        result = await agent.execute({"code": "x = 1", "language": "python"})
        assert "score" in result.result
        assert 0 <= result.result["score"] <= 10

    async def test_missing_code_raises_error(self, llm_provider: LLMProvider):
        agent = CodeReviewAgent(llm_provider)
        with pytest.raises(AgentExecutionError):
            await agent.execute({"language": "python"})

    async def test_empty_input_raises_error(self, llm_provider: LLMProvider):
        agent = CodeReviewAgent(llm_provider)
        with pytest.raises(AgentExecutionError):
            await agent.execute({})


@pytest.mark.asyncio
class TestIssueClassificationAgent:
    """Tests for the IssueClassificationAgent."""

    async def test_execute_returns_result(self, llm_provider: LLMProvider):
        agent = IssueClassificationAgent(llm_provider)
        result = await agent.execute({
            "title": "Bug in login",
            "description": "Login fails on mobile",
        })
        assert result.success is True
        assert result.agent_name == "issue_classification_agent"

    async def test_result_has_category(self, llm_provider: LLMProvider):
        agent = IssueClassificationAgent(llm_provider)
        result = await agent.execute({
            "title": "App crashes",
            "description": "Crash on startup",
        })
        assert "category" in result.result
        assert "priority" in result.result
        assert "confidence" in result.result

    async def test_missing_fields_raises_error(self, llm_provider: LLMProvider):
        agent = IssueClassificationAgent(llm_provider)
        with pytest.raises(AgentExecutionError):
            await agent.execute({"title": "only title"})


@pytest.mark.asyncio
class TestSuggestionAgent:
    """Tests for the SuggestionAgent."""

    async def test_execute_returns_result(self, llm_provider: LLMProvider):
        agent = SuggestionAgent(llm_provider)
        result = await agent.execute({
            "code": "for i in range(len(lst)): print(lst[i])",
            "language": "python",
        })
        assert result.success is True
        assert result.agent_name == "suggestion_agent"

    async def test_result_has_suggestion(self, llm_provider: LLMProvider):
        agent = SuggestionAgent(llm_provider)
        result = await agent.execute({
            "code": "x = dict()\ny = list()",
            "language": "python",
        })
        assert "suggested_code" in result.result
        assert "improvements" in result.result


class TestAgentFactory:
    """Tests for the AgentFactory."""

    def test_create_review_agent(self, agent_factory: AgentFactory):
        agent = agent_factory.create("code_review")
        assert isinstance(agent, CodeReviewAgent)

    def test_create_classification_agent(self, agent_factory: AgentFactory):
        agent = agent_factory.create("issue_classification")
        assert isinstance(agent, IssueClassificationAgent)

    def test_create_suggestion_agent(self, agent_factory: AgentFactory):
        agent = agent_factory.create("suggestion")
        assert isinstance(agent, SuggestionAgent)

    def test_unknown_agent_raises_error(self, agent_factory: AgentFactory):
        with pytest.raises(AgentNotFoundError):
            agent_factory.create("nonexistent")

    def test_agent_caching(self, agent_factory: AgentFactory):
        agent1 = agent_factory.create("code_review")
        agent2 = agent_factory.create("code_review")
        assert agent1 is agent2

    def test_available_agents(self):
        agents = AgentFactory.available_agents()
        assert "code_review" in agents
        assert "issue_classification" in agents
        assert "suggestion" in agents

    def test_convenience_methods(self, agent_factory: AgentFactory):
        assert isinstance(agent_factory.get_review_agent(), CodeReviewAgent)
        assert isinstance(agent_factory.get_classification_agent(), IssueClassificationAgent)
        assert isinstance(agent_factory.get_suggestion_agent(), SuggestionAgent)
