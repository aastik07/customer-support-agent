"""
backend/agent.py

Agent interface layer for the FastAPI backend.

This is the single point of contact between the /chat endpoint
and the Microsoft Foundry CustomerSupportAgent.

When Foundry is configured (AZURE_FOUNDRY_ENDPOINT + AGENT_ID are set),
messages are sent to the real agent via the OpenAI Assistants API that
Foundry exposes. When not configured, a stub response is returned so
the rest of the stack can still be developed and tested.

Authentication:
    Uses DefaultAzureCredential — no API key needed in code.
    Run `az login` once locally; Managed Identity is used in Azure.

Required environment variables:
    AZURE_FOUNDRY_ENDPOINT      — e.g. https://your-endpoint.api.azureml.ms
    AGENT_ID                    — the agent ID shown in the Foundry portal
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
    return _project_client.get_openai_client()


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
                "Set AZURE_FOUNDRY_ENDPOINT and AGENT_ID in your .env file "
                "to enable the live agent."
            ),
            "thread_id": thread_id or "stub-thread",
            "stub": True,
        }

    # ── Live mode: send message to Foundry agent ──────────────────────────────
    client = _get_openai_client()

    # Create a new thread or reuse an existing one for multi-turn conversation.
    if thread_id and thread_id != "stub-thread":
        thread = client.beta.threads.retrieve(thread_id)
    else:
        thread = client.beta.threads.create()

    # Add the user's message to the thread.
    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=message.strip(),
    )

    # Start a run using the configured agent.
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=settings.agent_id,
    )

    # Poll until the run completes (or fails).
    reply_text = _poll_run(client, thread_id=thread.id, run_id=run.id)

    return {
        "reply": reply_text,
        "thread_id": thread.id,
        "stub": False,
    }


# ── Polling helper ────────────────────────────────────────────────────────────

_TERMINAL_STATES = {"completed", "failed", "cancelled", "expired"}
_POLL_INTERVAL_SECONDS = 1
_POLL_TIMEOUT_SECONDS = 60


def _poll_run(client, *, thread_id: str, run_id: str) -> str:
    """
    Poll a Foundry agent run until it reaches a terminal state,
    then return the assistant's reply text.

    Raises AgentError if the run fails, is cancelled, expires, or times out.
    """
    elapsed = 0

    while elapsed < _POLL_TIMEOUT_SECONDS:
        run = client.beta.threads.runs.retrieve(
            thread_id=thread_id,
            run_id=run_id,
        )

        if run.status == "completed":
            return _extract_reply(client, thread_id=thread_id)

        if run.status in _TERMINAL_STATES:
            raise AgentError(
                f"Agent run ended with status '{run.status}'. "
                "Please try again or contact support."
            )

        time.sleep(_POLL_INTERVAL_SECONDS)
        elapsed += _POLL_INTERVAL_SECONDS

    raise AgentError(
        "Agent did not respond in time. Please try again."
    )


def _extract_reply(client, *, thread_id: str) -> str:
    """
    Retrieve the most recent assistant message from the thread
    and return its text content.
    """
    messages = client.beta.threads.messages.list(
        thread_id=thread_id,
        order="desc",
        limit=1,
    )

    for msg in messages:
        if msg.role == "assistant":
            # Content is a list of content blocks; collect all text parts.
            parts = [
                block.text.value
                for block in msg.content
                if block.type == "text"
            ]
            return " ".join(parts).strip()

    raise AgentError("No assistant reply found in thread.")
