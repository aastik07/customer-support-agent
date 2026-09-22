"""
backend/agent.py

Agent interface layer for the FastAPI backend.

This is the single point of contact between the /chat endpoint
and the Microsoft Foundry CustomerSupportAgent.

When Foundry is configured (AZURE_FOUNDRY_ENDPOINT + AGENT_NAME are set),
messages are sent to the real agent via the Foundry Responses API
(client.responses.create). When not configured, a stub response is returned so
the rest of the stack can still be developed and tested.

Authentication:
    Uses DefaultAzureCredential — no API key needed in code.
    Run `az login` once locally; Managed Identity is used in Azure.

Required environment variables:
    AZURE_FOUNDRY_ENDPOINT      — e.g. https://your-endpoint.api.azureml.ms
    AGENT_NAME                  — e.g. CustomerSupportAgent
"""

from __future__ import annotations

import time

from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

from backend.config import settings


# ── Exceptions ────────────────────────────────────────────────────────────────

class AgentNotConfiguredError(Exception):
    """Raised when Foundry env vars are missing."""


class AgentError(Exception):
    """Raised when the Foundry agent returns an error or unexpected state."""


# ── Foundry client (lazy, module-level singleton) ─────────────────────────────

_project_client: AIProjectClient | None = None


def _get_openai_client():
    """
    Return an authenticated OpenAI client pointed at the Foundry endpoint.
    The client is created once and reused for the lifetime of the process.
    """
    global _project_client
    if _project_client is None:
        _project_client = AIProjectClient(
            endpoint=settings.azure_foundry_endpoint,
            credential=DefaultAzureCredential(),
        )
    return _project_client.get_openai_client(agent_name=settings.agent_name)


# ── Agent response ────────────────────────────────────────────────────────────

def get_agent_response(message: str, thread_id: str | None = None) -> dict:
    """
    Send a user message to the CustomerSupportAgent and return a reply.

    Parameters
    ----------
    message : str
        The user's chat message.
    thread_id : str | None
        Pass the thread_id returned from a previous call to continue
        the same conversation. Pass None to start a new thread.

    Returns
    -------
    dict
        {
            "reply"     : str   — the agent's response text
            "thread_id" : str   — pass this back on the next turn
            "stub"      : bool  — True only in stub mode
        }

    Raises
    ------
    ValueError
        If the message is empty.
    AgentError
        If the agent run fails or times out.
    """
    if not message or not message.strip():
        raise ValueError("Message cannot be empty.")

    # ── Stub mode: Foundry not yet configured ─────────────────────────────────
    if not settings.is_foundry_configured():
        return {
            "reply": (
                "Hi! I'm Aria, your NovaBuy support assistant. "
                "The AI backend is not yet connected — this is a stub response. "
                "Set AZURE_FOUNDRY_ENDPOINT and AGENT_NAME in your .env file "
                "to enable the live agent."
            ),
            "thread_id": thread_id or "stub-thread",
            "stub": True,
        }

    # ── Live mode: send message to Foundry agent ──────────────────────────────
    client = _get_openai_client()

    kwargs = {"input": message.strip()}
    if thread_id and thread_id != "stub-thread" and thread_id.startswith("resp_"):
        kwargs["previous_response_id"] = thread_id

    try:
        response = client.responses.create(**kwargs)
    except Exception as e:
        raise AgentError(f"Agent run failed: {str(e)}")

    reply_text = ""
    if hasattr(response, "output"):
        for item in response.output:
            if hasattr(item, "content") and item.content:
                for block in item.content:
                    if hasattr(block, "type") and block.type in ("text", "output_text"):
                        reply_text += getattr(block, "text", "")
                    elif isinstance(block, dict) and block.get("type") == "text":
                        reply_text += block.get("text", "")

    new_thread_id = getattr(response, "id", None) or "stub-thread"

    return {
        "reply": reply_text.strip() or "No response from agent.",
        "thread_id": new_thread_id,
        "stub": False,
    }
