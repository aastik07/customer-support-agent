"""
agent/agent_config.py

Foundry Agent configuration reference.
Reads all credentials from environment variables — never hardcoded.

NOTE: This file is a configuration reference only.
The active Foundry integration is handled by backend/agent.py,
which uses the Azure AI Projects SDK directly via settings from backend/config.py.

Authentication uses DefaultAzureCredential, which resolves in order:
  1. Azure CLI login (for local development — run `az login` once)
  2. Environment variables (AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, AZURE_TENANT_ID)
  3. Managed Identity (when deployed to Azure)
"""

import os
from pathlib import Path
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential


# ── Environment variables (set in .env, never committed) ──────────────────────

AZURE_FOUNDRY_ENDPOINT: str = os.getenv("AZURE_FOUNDRY_ENDPOINT", "")
AZURE_FOUNDRY_PROJECT_NAME: str = os.getenv("AZURE_FOUNDRY_PROJECT_NAME", "")
AGENT_NAME: str = os.getenv("AGENT_NAME", "CustomerSupportAgent")
AGENT_MODEL: str = os.getenv("AGENT_MODEL", "gpt-4o")

# ── System prompt ─────────────────────────────────────────────────────────────

_PROMPT_PATH = Path(__file__).parent / "system_prompt.md"
SYSTEM_PROMPT: str = _PROMPT_PATH.read_text(encoding="utf-8")

# ── Foundry client ────────────────────────────────────────────────────────────

def get_project_client() -> AIProjectClient:
    """
    Return an authenticated AIProjectClient for the Foundry project.

    The active backend integration (backend/agent.py) creates its own
    client internally via the same credential chain. This helper is
    retained here for ad-hoc scripts and manual testing.
    """
    return AIProjectClient(
        endpoint=AZURE_FOUNDRY_ENDPOINT,
        credential=DefaultAzureCredential(),
    )
