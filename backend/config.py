"""
backend/config.py

Centralised configuration for the FastAPI backend.
All values are read from environment variables (set in .env locally).
Nothing is hardcoded.

Usage:
    from backend.config import settings
    print(settings.agent_name)
"""

import os
from functools import lru_cache
from dotenv import load_dotenv

# Load .env file if present (no-op in production where env vars are set directly).
load_dotenv()


class Settings:
    """
    Application settings resolved from environment variables.
    Raises KeyError at startup if a required variable is missing,
    making misconfiguration fail fast and loudly.
    """

    # ── FastAPI ───────────────────────────────────────────────────────────────
    host: str = os.getenv("BACKEND_HOST", "0.0.0.0")
    port: int = int(os.getenv("BACKEND_PORT", "8000"))
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"

    # ── Microsoft Foundry (not used until Phase 2 integration) ────────────────
    azure_foundry_endpoint: str = os.getenv("AZURE_FOUNDRY_ENDPOINT", "")
    azure_foundry_project_name: str = os.getenv("AZURE_FOUNDRY_PROJECT_NAME", "")
    agent_name: str = os.getenv("AGENT_NAME", "")
    agent_model: str = os.getenv("AGENT_MODEL", "gpt-4o")

    # ── Foundry IQ / RAG (not used until Phase 3) ─────────────────────────────
    search_index_name: str = os.getenv("SEARCH_INDEX_NAME", "")
    search_endpoint: str = os.getenv("SEARCH_ENDPOINT", "")

    # ── Custom Tool API authentication ────────────────────────────────────────
    # The four custom-tool endpoints (/orders, /customers, /refunds, /tickets)
    # are protected by an API key supplied in the x-api-key request header.
    # Microsoft Foundry reads this key from its OpenAPI tool configuration.
    # Never hardcode this value — always read it from the environment.
    customer_support_api_key: str = os.getenv("CUSTOMER_SUPPORT_API_KEY", "")

    def is_foundry_configured(self) -> bool:
        """Return True if the minimum Foundry env vars have been set."""
        return bool(self.azure_foundry_endpoint and self.agent_name)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Return a cached Settings instance.
    The cache means .env is only read once per process.
    """
    return Settings()


# Module-level shortcut for convenience.
settings = get_settings()
