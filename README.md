# 🧠 GenAI Developer Productivity Agent

A **production-grade AI-powered developer assistant backend** that performs code review, issue classification, and intelligent code suggestion generation using modular LLM agent workflows.

Built with **FastAPI**, **Python 3.11+**, and a clean modular architecture implementing **Factory**, **Strategy**, and **Observer** design patterns.

[![CI Pipeline](https://github.com/yourusername/genai-developer-agent/actions/workflows/ci.yml/badge.svg)](https://github.com/yourusername/genai-developer-agent/actions)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 📋 Table of Contents

1. [Project Overview](#-project-overview)
2. [System Architecture](#-system-architecture)
3. [AI Agent Workflow](#-ai-agent-workflow)
4. [API Design](#-api-design)
5. [LLM Integration Strategy](#-llm-integration-strategy)
6. [Design Patterns Used](#-design-patterns-used)
7. [Setup Instructions](#-setup-instructions)
8. [Docker Deployment Guide](#-docker-deployment-guide)
9. [Example Requests/Responses](#-example-requestsresponses)
10. [Monitoring & Observability](#-monitoring--observability)
11. [Benchmark Results](#-benchmark-results)
12. [Future Improvements](#-future-improvements)

---

## 🔭 Project Overview

The GenAI Developer Productivity Agent is a scalable AI SaaS backend platform that provides:

| Feature | Description |
|---------|-------------|
| **Code Review** | Analyzes code for bugs, anti-patterns, security issues, and style violations |
| **Issue Classification** | Categorizes developer issues/tickets with priority estimation and confidence scores |
| **Code Suggestions** | Generates refactored/optimized code with detailed improvement explanations |
| **Health Monitoring** | Real-time health checks, metrics aggregation, and alerting |

### Key Capabilities

- ⚡ **Async-first** — Built on ASGI with full async/await support
- 🔌 **Pluggable LLM** — Swap between OpenAI and local simulation without code changes
- 🏭 **Factory Pattern** — Dynamic agent registration and creation
- 🎯 **Strategy Pattern** — Runtime LLM provider selection
- 👁️ **Observer Pattern** — Decoupled monitoring and alerting
- 🐳 **Docker-ready** — Production container with health checks
- 📊 **Built-in metrics** — Latency percentiles, throughput, error rates
- 🔄 **Resilient** — Retry logic, timeouts, graceful error handling

---

## 🏗️ System Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                      Client Layer                             │
│               HTTP Client / CLI / SDK                         │
└────────────────────────┬─────────────────────────────────────┘
                         │
┌────────────────────────▼─────────────────────────────────────┐
│                    Middleware Layer                            │
│         RequestLogger ─── ErrorHandler ─── CORS               │
└────────────────────────┬─────────────────────────────────────┘
                         │
┌────────────────────────▼─────────────────────────────────────┐
│                   API Layer (FastAPI)                          │
│    POST /review  │  POST /classify  │  POST /suggest          │
│    GET /health   │  GET /metrics                              │
└────────────────────────┬─────────────────────────────────────┘
                         │
┌────────────────────────▼─────────────────────────────────────┐
│                   Service Layer                               │
│    ReviewService  │  ClassificationService  │  SuggestionSvc  │
└────────────────────────┬─────────────────────────────────────┘
                         │
┌────────────────────────▼─────────────────────────────────────┐
│              Agent Orchestration (Factory Pattern)             │
│    CodeReviewAgent  │  IssueClassAgent  │  SuggestionAgent    │
└────────────────────────┬─────────────────────────────────────┘
                         │
┌────────────────────────▼──────────────┐  ┌───────────────────┐
│     LLM Integration (Strategy)        │  │  Prompt Templates  │
│   OpenAIProvider ◄──► LocalProvider   │  │  Review │ Classify │
└───────────────────────────────────────┘  └───────────────────┘
                         │
┌────────────────────────▼─────────────────────────────────────┐
│             Observability (Observer Pattern)                   │
│    EventBus ──► MetricsListener │ LoggingListener │ Alerts    │
└──────────────────────────────────────────────────────────────┘
```

### Project Structure

```
genai-developer-agent/
├── app/
│   ├── api/              # FastAPI routes and dependency injection
│   ├── agents/           # AI agent implementations (Factory Pattern)
│   ├── core/             # Configuration, exceptions, logging
│   ├── middleware/        # Request logging, error handling
│   ├── models/           # Pydantic request/response schemas
│   ├── monitoring/       # Observability (Observer Pattern)
│   ├── prompts/          # LLM prompt template management
│   ├── services/         # Business logic + LLM integration (Strategy)
│   └── utils/            # Shared helpers and decorators
├── tests/                # pytest test suite
├── scripts/              # Dev server, benchmarks
├── configs/              # YAML configuration
├── docker/               # Docker support files
├── docs/                 # Architecture documentation
├── examples/             # API usage examples
├── .github/workflows/    # CI/CD pipeline
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

## 🤖 AI Agent Workflow

```
User Request ──► API Route ──► Service Layer ──► AgentFactory.create()
                                                        │
                                                        ▼
                                                   BaseAgent.execute()
                                                        │
                                           ┌────────────┼────────────┐
                                           ▼            ▼            ▼
                                     CodeReview    Classify     Suggestion
                                       Agent        Agent         Agent
                                           │            │            │
                                           ▼            ▼            ▼
                                     PromptTemplate.render()
                                           │
                                           ▼
                                     LLMProvider.generate()
                                           │
                                           ▼
                                     Parse JSON Response
                                           │
                                           ▼
                                     AgentResult ──► Service ──► API Response
```

Each agent:
1. **Validates** input data
2. **Renders** domain-specific prompts from templates
3. **Calls** the LLM provider (OpenAI or local simulation)
4. **Parses** the structured JSON response
5. **Returns** an `AgentResult` with execution metadata

---

## 📡 API Design

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/review` | Analyze code for issues and anti-patterns |
| `POST` | `/classify` | Classify an issue with priority estimation |
| `POST` | `/suggest` | Generate optimized code suggestions |
| `GET`  | `/health` | System health check |
| `GET`  | `/metrics` | Application metrics and performance data |

All endpoints are also available under `/api/v1/` prefix.

### Interactive Documentation

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

---

## 🔌 LLM Integration Strategy

The system uses the **Strategy Pattern** to abstract LLM provider details:

```python
# Abstract interface
class LLMProvider(ABC):
    async def generate(self, request: LLMRequest) -> LLMResponse: ...
    async def health_check(self) -> bool: ...

# Concrete strategies
class OpenAIProvider(LLMProvider): ...      # Real API calls
class LocalSimulationProvider(LLMProvider): ...  # Mock responses
```

### Provider Selection

```bash
# Use local simulation (default — no API key needed)
LLM_PROVIDER=local

# Use OpenAI
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here
```

The **Local Simulation Provider** generates realistic, context-aware responses by analyzing prompt content. It detects patterns like `eval()`, bare `except:`, and hardcoded credentials to produce relevant code review findings.

---

## 🧱 Design Patterns Used

### 1. Factory Pattern — Agent Orchestration

```python
# Register agents dynamically
AgentFactory.register("custom_agent", CustomAgent)

# Create agents by type
agent = factory.create("code_review")  # Returns CodeReviewAgent
agent = factory.create("custom_agent") # Returns CustomAgent
```

**Where**: `app/agents/factory.py`
**Why**: Decouples agent creation from business logic. New agents can be added without modifying existing code.

### 2. Strategy Pattern — LLM Provider Abstraction

```python
# Swap provider at runtime via config
provider = LLMProviderFactory.create("openai")  # or "local"

# All providers share the same interface
response = await provider.generate(LLMRequest(prompt="..."))
```

**Where**: `app/services/llm/`
**Why**: Agents are agnostic to the underlying LLM. Switch between OpenAI and local simulation with a single config change.

### 3. Observer Pattern — Monitoring Hooks

```python
# Subscribe to events
event_bus.subscribe(EventType.REQUEST_COMPLETED, metrics_listener.handle)
event_bus.subscribe(None, logging_listener.handle)  # All events

# Publish from anywhere
await event_bus.publish(RequestEvent(endpoint="/review", latency_ms=150))
```

**Where**: `app/monitoring/`
**Why**: Services emit events without knowing who listens. Metrics, logging, and alerting are decoupled from business logic.

---

## ⚙️ Setup Instructions

### Prerequisites

- Python 3.11+
- pip

### Quick Start

```bash
# Clone the repository
git clone https://github.com/yourusername/genai-developer-agent.git
cd genai-developer-agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Copy environment config
cp .env.example .env

# Start the development server
python scripts/run_dev.py
```

The API will be available at `http://localhost:8000`.

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=app --cov-report=term-missing

# Run specific test file
pytest tests/test_agents.py -v
```

---

## 🐳 Docker Deployment Guide

### Build and Run

```bash
# Build the Docker image
docker build -t genai-developer-agent .

# Run the container
docker run -p 8000:8000 genai-developer-agent

# Or use Docker Compose
docker-compose up -d
```

### Production Deployment

```bash
# Build for production
docker-compose -f docker-compose.yml up -d

# Check logs
docker-compose logs -f genai-agent

# Check health
curl http://localhost:8000/health
```

### Container Features

- Multi-stage build for minimal image size
- Non-root user for security
- Built-in health check
- Resource limits (1GB RAM, 2 CPUs)
- Auto-restart on failure

---

## 📝 Example Requests/Responses

### Code Review

```bash
curl -X POST http://localhost:8000/review \
  -H "Content-Type: application/json" \
  -d '{
    "code": "def process(data):\n    result = eval(data)\n    return result",
    "language": "python",
    "context": "Data processing function"
  }'
```

**Response:**
```json
{
  "issues": [
    {
      "severity": "critical",
      "line": null,
      "message": "Use of eval() detected — potential code injection vulnerability",
      "category": "security",
      "suggestion": "Replace with ast.literal_eval() or a safer alternative"
    }
  ],
  "summary": "Analyzed 3 lines of code. Found 1 issue(s).",
  "score": 4.5,
  "suggestions": ["Add comprehensive error handling"],
  "language": "python",
  "lines_analyzed": 3,
  "execution_time_ms": 215.43
}
```

### Issue Classification

```bash
curl -X POST http://localhost:8000/classify \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Login page crashes on mobile Safari",
    "description": "The page crashes immediately after loading on iOS Safari 17.2"
  }'
```

**Response:**
```json
{
  "category": "bug",
  "priority": "critical",
  "confidence": 0.95,
  "reasoning": "The issue description indicates a bug concern with critical priority.",
  "suggested_labels": ["bug", "critical", "needs-triage"],
  "execution_time_ms": 198.21
}
```

### Code Suggestions

```bash
curl -X POST http://localhost:8000/suggest \
  -H "Content-Type: application/json" \
  -d '{
    "code": "for i in range(len(lst)):\n    print(lst[i])",
    "language": "python",
    "instruction": "Use Pythonic idioms"
  }'
```

**Response:**
```json
{
  "original_code": "for i in range(len(lst)):\n    print(lst[i])",
  "suggested_code": "for i, item in enumerate(lst):\n    logger.info(item)",
  "explanation": "Applied 2 improvement(s) focusing on Python best practices.",
  "improvements": [
    "Replaced 'for i in range(len(' with 'for i, item in enumerate(' for better idioms",
    "Replaced 'print(' with 'logger.info(' for production logging"
  ],
  "language": "python",
  "execution_time_ms": 205.67
}
```

---

## 📊 Monitoring & Observability

### Health Check

```bash
GET /health
```

Returns system status, LLM provider health, loaded agents, and uptime.

### Metrics

```bash
GET /metrics
```

Returns:
- **Total requests** and per-endpoint breakdown
- **Latency percentiles** (avg, P50, P95, P99)
- **Error count** and error rate
- **Agent execution times** per agent type
- **Active requests** and uptime

### Structured Logging

All logs are JSON-formatted with:
- Request correlation IDs (`X-Request-ID` header)
- Timestamps (ISO 8601)
- Log level, logger name, and contextual metadata

### Alert System

The `AlertListener` triggers warnings when:
- Error count exceeds threshold within a 60-second window
- Request latency exceeds the configured threshold

---

## 📈 Benchmark Results

Run benchmarks with:

```bash
python scripts/benchmark.py --concurrency 10 --requests 50
```

### Expected Results (Local Provider)

| Endpoint | Avg Latency | P95 Latency | P99 Latency | Throughput |
|----------|------------|------------|------------|------------|
| GET /health | ~5ms | ~10ms | ~15ms | ~2000 req/s |
| GET /metrics | ~3ms | ~8ms | ~12ms | ~2500 req/s |
| POST /review | ~220ms | ~280ms | ~310ms | ~45 req/s |
| POST /classify | ~210ms | ~270ms | ~300ms | ~47 req/s |
| POST /suggest | ~215ms | ~275ms | ~305ms | ~46 req/s |

- **Success Rate**: ~100% (local provider)
- **Concurrent Handling**: 10+ simultaneous requests
- **Simulated Accuracy**: ~90%+ on pattern detection

> **Note:** Agent endpoint latency is dominated by the simulated LLM delay (~200ms). With the local provider, actual processing is <5ms.

---

## 🚀 Future Improvements

- [ ] **Streaming responses** — SSE/WebSocket for real-time agent output
- [ ] **Redis queue** — Async task processing for long-running analyses
- [ ] **Multi-model routing** — Route to different LLMs based on task complexity
- [ ] **Agent chaining** — Sequential multi-agent workflows (review → suggest)
- [ ] **Caching layer** — Redis-based response caching for identical inputs
- [ ] **Rate limiting** — Per-client rate limits with token bucket
- [ ] **Authentication** — JWT/API key authentication middleware
- [ ] **Prometheus exporter** — Native Prometheus metrics endpoint
- [ ] **OpenTelemetry** — Distributed tracing integration
- [ ] **Fine-tuned models** — Custom models for domain-specific reviews
- [ ] **Plugin system** — Third-party agent registration via entry points
- [ ] **Web dashboard** — Real-time monitoring UI

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

<div align="center">

**Built with ❤️ using FastAPI, Python 3.11+, and modern AI architecture patterns**

</div>
