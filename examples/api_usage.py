"""
Example API usage script — demonstrates all endpoints.

Usage:
    1. Start the server: python scripts/run_dev.py
    2. Run this script: python examples/api_usage.py
"""

from __future__ import annotations

import asyncio
import json
import sys

import httpx

BASE_URL = "http://localhost:8000"


def pretty_print(title: str, data: dict) -> None:
    """Pretty print a response."""
    print(f"\n{'═' * 60}")
    print(f"  {title}")
    print(f"{'═' * 60}")
    print(json.dumps(data, indent=2, default=str))


async def main() -> None:
    """Run all API examples."""
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:

        # ── Health Check ──
        print("\n🏥 Checking API health...")
        resp = await client.get("/health")
        pretty_print("GET /health", resp.json())

        # ── Code Review ──
        print("\n🔍 Submitting code for review...")
        review_resp = await client.post("/review", json={
            "code": """
def process_user_data(data):
    results = []
    for i in range(len(data)):
        if data[i] != None:
            try:
                val = eval(str(data[i]))
                results.append(val)
            except:
                pass
    
    password = "secret123"
    global shared_state
    shared_state = results
    return results
""",
            "language": "python",
            "context": "User data processing pipeline",
            "strict_mode": False,
        })
        pretty_print("POST /review", review_resp.json())

        # ── Issue Classification ──
        print("\n🏷️ Classifying an issue...")
        classify_resp = await client.post("/classify", json={
            "title": "Authentication service crashes under high load",
            "description": (
                "When the authentication service receives more than 1000 concurrent "
                "login requests, it crashes with an OutOfMemoryError. The issue is "
                "reproducible in staging and has been observed in production during "
                "peak hours. This is blocking our Black Friday preparations."
            ),
            "labels": ["backend", "production"],
        })
        pretty_print("POST /classify", classify_resp.json())

        # ── Code Suggestions ──
        print("\n💡 Generating code suggestions...")
        suggest_resp = await client.post("/suggest", json={
            "code": """
def find_duplicates(lst):
    duplicates = []
    for i in range(len(lst)):
        for j in range(i + 1, len(lst)):
            if lst[i] == lst[j]:
                if lst[i] not in duplicates:
                    duplicates.append(lst[i])
    return duplicates

def get_user(users, user_id):
    for i in range(len(users)):
        if users[i]["id"] == user_id:
            return users[i]
    return None
""",
            "language": "python",
            "instruction": "Optimize for performance and use Pythonic idioms",
            "focus_areas": ["performance", "readability"],
        })
        pretty_print("POST /suggest", suggest_resp.json())

        # ── Metrics ──
        print("\n📊 Fetching metrics...")
        metrics_resp = await client.get("/metrics")
        pretty_print("GET /metrics", metrics_resp.json())

        print("\n✅ All examples completed successfully!")
        print(f"📖 API Documentation: {BASE_URL}/docs")
        print(f"📖 ReDoc: {BASE_URL}/redoc\n")


if __name__ == "__main__":
    asyncio.run(main())
