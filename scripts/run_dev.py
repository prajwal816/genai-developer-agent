"""
Development server launcher.

Usage:
    python scripts/run_dev.py
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import uvicorn

from app.core.config import get_settings


def main() -> None:
    """Launch the development server."""
    settings = get_settings()

    print(f"""
╔══════════════════════════════════════════════════════════════╗
║       GenAI Developer Productivity Agent — Dev Server        ║
╠══════════════════════════════════════════════════════════════╣
║  Version:      {settings.app_version:<44s}║
║  LLM Provider: {settings.llm.provider:<44s}║
║  Debug:        {str(settings.app_debug):<44s}║
║  Docs:         http://{settings.app_host}:{settings.app_port}/docs{' ' * 26}║
╚══════════════════════════════════════════════════════════════╝
    """)

    uvicorn.run(
        "app.main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=True,
        log_level="info",
    )


if __name__ == "__main__":
    main()
