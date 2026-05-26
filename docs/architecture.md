# Architecture Documentation

## System Overview

The GenAI Developer Productivity Agent is a production-grade AI-powered backend platform built with FastAPI. It provides three core AI agent capabilities: **Code Review**, **Issue Classification**, and **Code Suggestion Generation**.

## Layered Architecture

```
┌─────────────────────────────────────────────┐
│              Client Layer                    │
│         (HTTP / CLI / SDK)                   │
├─────────────────────────────────────────────┤
│           Middleware Layer                    │
│   RequestLogger │ ErrorHandler │ CORS        │
├─────────────────────────────────────────────┤
│             API Layer (FastAPI)               │
│   /review │ /classify │ /suggest             │
│   /health │ /metrics                         │
├─────────────────────────────────────────────┤
│            Service Layer                     │
│   ReviewService │ ClassificationService      │
│   SuggestionService                          │
├─────────────────────────────────────────────┤
│         Agent Orchestration                  │
│   AgentFactory (Factory Pattern)             │
│   CodeReviewAgent │ IssueClassAgent          │
│   SuggestionAgent                            │
├─────────────────────────────────────────────┤
│          LLM Integration                     │
│   LLMProviderFactory                         │
│   OpenAIProvider │ LocalProvider             │
│   (Strategy Pattern)                         │
├─────────────────────────────────────────────┤
│          Observability                       │
│   EventBus (Observer Pattern)                │
│   MetricsListener │ LoggingListener          │
│   AlertListener                              │
└─────────────────────────────────────────────┘
```

## Design Patterns

### Factory Pattern — Agent Orchestration
- `AgentFactory` creates agents by type key
- Dynamic registration without modifying factory
- Instance caching for performance

### Strategy Pattern — LLM Providers
- `LLMProvider` abstract interface
- `OpenAIProvider` and `LocalSimulationProvider` as concrete strategies
- Runtime provider swapping via configuration

### Observer Pattern — Monitoring
- `EventBus` is the Subject (singleton)
- Listeners are Observers: Metrics, Logging, Alerting
- Decoupled — services emit events without knowing who listens

## Data Flow

1. Client sends HTTP request
2. `RequestLoggingMiddleware` assigns correlation ID, emits `REQUEST_STARTED`
3. FastAPI routes to handler → injects service via DI
4. Service uses `AgentFactory` to create/retrieve agent
5. Agent renders prompt template → calls `LLMProvider.generate()`
6. LLM response is parsed → structured result returned
7. Service emits `AGENT_EXECUTION_COMPLETED` via EventBus
8. Middleware emits `REQUEST_COMPLETED` with latency
9. Listeners update metrics, log structured data, check alerts
10. JSON response returned to client

## Resilience Mechanisms

- **Retry**: `tenacity` exponential backoff on LLM provider calls
- **Timeouts**: Configurable per-agent and per-provider
- **Error Isolation**: EventBus listener errors don't propagate
- **Graceful Degradation**: Health check reports "degraded" if LLM is down
- **Structured Errors**: All exceptions mapped to JSON with error codes
