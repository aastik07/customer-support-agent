"""
agent/agent_config.py

Foundry Agent configuration and client initialisation.
Reads all credentials from environment variables — never hardcoded.

Used by the FastAPI backend to get a ready-to-use agent client.
"""

import os
from pathlib import Path
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential


# ── Environment variables (set in .env, never committed) ──────────────────────

AZURE_FOUNDRY_ENDPOINT: str = os.environ["AZURE_FOUNDRY_ENDPOINT"]
AZURE_FOUNDRY_PROJECT_NAME: str = os.environ["AZURE_FOUNDRY_PROJECT_NAME"]
AGENT_ID: str = os.environ["AGENT_ID"]
AGENT_MODEL: str = os.getenv("AGENT_MODEL", "gpt-4o")

# ── System prompt ─────────────────────────────────────────────────────────────

_PROMPT_PATH = Path(__file__).parent / "system_prompt.md"
SYSTEM_PROMPT: str = _PROMPT_PATH.read_text(encoding="utf-8")

# ── Foundry client ────────────────────────────────────────────────────────────

def get_project_client() -> AIProjectClient:
    """
    Return an authenticated AIProjectClient.

    Authentication uses DefaultAzureCredential, which resolves in order:
      1. Environment variables (AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, AZURE_TENANT_ID)
      2. Managed Identity (when deployed to Azure)
      3. Azure CLI login (for local development — run `az login` once)
    """
    return AIProjectClient(
        endpoint=AZURE_FOUNDRY_ENDPOINT,
        credential=DefaultAzureCredential(),
    )
