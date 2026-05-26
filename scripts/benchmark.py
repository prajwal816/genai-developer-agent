"""
Benchmark script — measures API performance under concurrent load.

Usage:
    python scripts/benchmark.py [--base-url http://localhost:8000] [--concurrency 10] [--requests 50]
"""

from __future__ import annotations

import argparse
import asyncio
import json
import statistics
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import httpx


@dataclass
class BenchmarkResult:
    """Results from a single endpoint benchmark."""

    endpoint: str
    total_requests: int = 0
    successful: int = 0
    failed: int = 0
    latencies: list[float] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    @property
    def success_rate(self) -> float:
        if self.total_requests == 0:
            return 0.0
        return self.successful / self.total_requests * 100

    @property
    def avg_latency(self) -> float:
        return statistics.mean(self.latencies) if self.latencies else 0.0

    @property
    def p50_latency(self) -> float:
        return statistics.median(self.latencies) if self.latencies else 0.0

    @property
    def p95_latency(self) -> float:
        if not self.latencies:
            return 0.0
        sorted_l = sorted(self.latencies)
        idx = int(len(sorted_l) * 0.95)
        return sorted_l[min(idx, len(sorted_l) - 1)]

    @property
    def p99_latency(self) -> float:
        if not self.latencies:
            return 0.0
        sorted_l = sorted(self.latencies)
        idx = int(len(sorted_l) * 0.99)
        return sorted_l[min(idx, len(sorted_l) - 1)]

    @property
    def throughput(self) -> float:
        if not self.latencies:
            return 0.0
        total_time = sum(self.latencies) / 1000
        return self.total_requests / max(total_time, 0.001)


# Test payloads
REVIEW_PAYLOAD = {
    "code": """
def process_data(data):
    result = []
    for i in range(len(data)):
        if data[i] != None:
            try:
                val = eval(str(data[i]))
                result.append(val)
            except:
                pass
    return result

password = "admin123"
global_state = {}
""",
    "language": "python",
    "context": "Data processing utility function",
}

CLASSIFY_PAYLOAD = {
    "title": "Login page crashes on mobile Safari",
    "description": (
        "When accessing the login page on iOS Safari (version 17.2), "
        "the page crashes immediately after loading. The console shows "
        "a JavaScript error related to the authentication module. "
        "This affects all mobile users and is blocking production deployments."
    ),
    "labels": ["mobile", "urgent"],
}

SUGGEST_PAYLOAD = {
    "code": """
def find_duplicates(lst):
    duplicates = []
    for i in range(len(lst)):
        for j in range(i + 1, len(lst)):
            if lst[i] == lst[j]:
                if lst[i] not in duplicates:
                    duplicates.append(lst[i])
    return duplicates
""",
    "language": "python",
    "instruction": "Optimize for performance",
}


async def benchmark_endpoint(
    client: httpx.AsyncClient,
    method: str,
    url: str,
    payload: dict | None,
    num_requests: int,
    concurrency: int,
) -> BenchmarkResult:
    """Benchmark a single endpoint with concurrent requests."""
    result = BenchmarkResult(endpoint=url)
    semaphore = asyncio.Semaphore(concurrency)

    async def make_request() -> None:
        async with semaphore:
            start = time.perf_counter()
            try:
                if method == "GET":
                    resp = await client.get(url)
                else:
                    resp = await client.post(url, json=payload)

                latency = (time.perf_counter() - start) * 1000
                result.total_requests += 1
                result.latencies.append(latency)

                if resp.status_code < 400:
                    result.successful += 1
                else:
                    result.failed += 1
                    result.errors.append(f"HTTP {resp.status_code}")

            except Exception as e:
                result.total_requests += 1
                result.failed += 1
                result.errors.append(str(e))
                result.latencies.append((time.perf_counter() - start) * 1000)

    tasks = [make_request() for _ in range(num_requests)]
    await asyncio.gather(*tasks)
    return result


def print_result(result: BenchmarkResult) -> None:
    """Pretty print benchmark results for a single endpoint."""
    status = "✅" if result.success_rate >= 95 else "⚠️" if result.success_rate >= 80 else "❌"

    print(f"\n{'─' * 60}")
    print(f"  {status} {result.endpoint}")
    print(f"{'─' * 60}")
    print(f"  Requests:     {result.total_requests}")
    print(f"  Successful:   {result.successful} ({result.success_rate:.1f}%)")
    print(f"  Failed:       {result.failed}")
    print(f"  Avg Latency:  {result.avg_latency:.2f}ms")
    print(f"  P50 Latency:  {result.p50_latency:.2f}ms")
    print(f"  P95 Latency:  {result.p95_latency:.2f}ms")
    print(f"  P99 Latency:  {result.p99_latency:.2f}ms")
    print(f"  Throughput:   {result.throughput:.1f} req/s")
    if result.errors:
        unique_errors = set(result.errors[:5])
        print(f"  Errors:       {', '.join(unique_errors)}")


async def run_benchmark(base_url: str, concurrency: int, num_requests: int) -> None:
    """Run the full benchmark suite."""
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║         GenAI Agent — Performance Benchmark Suite            ║
╠══════════════════════════════════════════════════════════════╣
║  Base URL:     {base_url:<44s}║
║  Concurrency:  {str(concurrency):<44s}║
║  Requests/EP:  {str(num_requests):<44s}║
╚══════════════════════════════════════════════════════════════╝
    """)

    endpoints = [
        ("GET", f"{base_url}/health", None),
        ("GET", f"{base_url}/metrics", None),
        ("POST", f"{base_url}/review", REVIEW_PAYLOAD),
        ("POST", f"{base_url}/classify", CLASSIFY_PAYLOAD),
        ("POST", f"{base_url}/suggest", SUGGEST_PAYLOAD),
    ]

    all_results: list[BenchmarkResult] = []

    async with httpx.AsyncClient(timeout=60.0) as client:
        for method, url, payload in endpoints:
            print(f"\n⏳ Benchmarking {method} {url}...")
            result = await benchmark_endpoint(
                client, method, url, payload, num_requests, concurrency
            )
            print_result(result)
            all_results.append(result)

    # Summary
    total_requests = sum(r.total_requests for r in all_results)
    total_success = sum(r.successful for r in all_results)
    all_latencies = [l for r in all_results for l in r.latencies]

    print(f"\n{'═' * 60}")
    print(f"  📊 BENCHMARK SUMMARY")
    print(f"{'═' * 60}")
    print(f"  Total Requests:    {total_requests}")
    print(f"  Total Successful:  {total_success} ({total_success/max(total_requests,1)*100:.1f}%)")
    print(f"  Overall Avg:       {statistics.mean(all_latencies):.2f}ms")
    print(f"  Overall P95:       {sorted(all_latencies)[int(len(all_latencies)*0.95)]:.2f}ms" if all_latencies else "")
    print(f"  Simulated Accuracy: ~{total_success/max(total_requests,1)*100:.0f}%")
    print(f"{'═' * 60}\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="GenAI Agent Benchmark")
    parser.add_argument("--base-url", default="http://localhost:8000", help="API base URL")
    parser.add_argument("--concurrency", type=int, default=10, help="Concurrent requests")
    parser.add_argument("--requests", type=int, default=50, help="Requests per endpoint")
    args = parser.parse_args()

    asyncio.run(run_benchmark(args.base_url, args.concurrency, args.requests))


if __name__ == "__main__":
    main()
