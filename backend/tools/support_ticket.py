"""
backend/tools/support_ticket.py

Custom tool: create_support_ticket
Generates a fictional support ticket for a customer and returns
structured ticket information the agent can relay to the customer.

Tickets are not persisted — this is a mock implementation for
demonstration purposes. No database or external service is required.

Used by the Foundry Agent as a registered tool function.
Does not connect to Microsoft Foundry directly.
"""

import random
import string
import uuid
from datetime import datetime, timezone, timedelta
from typing import Any

# ── Constants ─────────────────────────────────────────────────────────────────

# SLA: support team responds within this many business hours.
_RESPONSE_SLA_HOURS = 4

# Estimated resolution target in business days.
_RESOLUTION_SLA_DAYS = 2


# ── Helpers ───────────────────────────────────────────────────────────────────

def _generate_ticket_id() -> str:
    """
    Generate a short, human-readable support ticket ID.
    Format: TKT-XXXXXX  (6 uppercase alphanumeric characters)
    Example: TKT-A3F9K2
    """
    chars = string.ascii_uppercase + string.digits
    suffix = "".join(random.choices(chars, k=6))
    return f"TKT-{suffix}"


def _utc_now() -> datetime:
    """Return the current UTC time as a timezone-aware datetime."""
    return datetime.now(tz=timezone.utc)


def _format_dt(dt: datetime) -> str:
    """Format a datetime as an ISO 8601 string (UTC, no microseconds)."""
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


# ── Tool function ─────────────────────────────────────────────────────────────

def create_support_ticket(customer_id: str, issue: str) -> dict[str, Any]:
    """
    Create a support ticket on behalf of a customer.

    Parameters
    ----------
    customer_id : str
        The ID of the customer raising the ticket (e.g. "CUST-00391").
    issue : str
        A plain-text description of the customer's issue, as understood
        by the agent from the conversation.

    Returns
    -------
    dict
        On success:
            {
                "success": True,
                "ticket_id": str,
                "customer_id": str,
                "issue_summary": str,
                "status": str,
                "created_at": str (ISO 8601 UTC),
                "expected_response_by": str (ISO 8601 UTC),
                "message": str
            }

        On failure (invalid input):
            {
                "success": False,
                "customer_id": str,
                "error": str
            }
    """
    # ── Input validation ──────────────────────────────────────────────────────

    if not customer_id or not isinstance(customer_id, str):
        return {
            "success": False,
            "customer_id": customer_id,
            "error": "Invalid customer ID. Please provide a valid customer ID.",
        }

    if not issue or not isinstance(issue, str):
        return {
            "success": False,
            "customer_id": customer_id,
            "error": "Issue description cannot be empty. Please describe the problem.",
        }

    issue_stripped = issue.strip()
    if len(issue_stripped) < 5:
        return {
            "success": False,
            "customer_id": customer_id,
            "error": "Issue description is too short. Please provide more detail.",
        }

    # ── Generate ticket ───────────────────────────────────────────────────────

    ticket_id = _generate_ticket_id()
    created_at = _utc_now()
    expected_response_by = created_at + timedelta(hours=_RESPONSE_SLA_HOURS)

    # Truncate very long issue descriptions to a clean summary.
    issue_summary = issue_stripped if len(issue_stripped) <= 200 else issue_stripped[:197] + "..."

    return {
        "success": True,
        "ticket_id": ticket_id,
        "customer_id": customer_id.strip().upper(),
        "issue_summary": issue_summary,
        "status": "Open",
        "created_at": _format_dt(created_at),
        "expected_response_by": _format_dt(expected_response_by),
        "message": (
            f"Your support ticket has been created successfully. "
            f"Your ticket reference is {ticket_id}. "
            f"A member of our support team will respond within "
            f"{_RESPONSE_SLA_HOURS} business hours. "
            f"Please keep your ticket reference handy when following up."
        ),
    }


# ── Quick manual test ─────────────────────────────────────────────────────────

if __name__ == "__main__":
    import json

    test_cases = [
        # Valid tickets
        ("CUST-00391", "My order NB-1042873 was delivered but the item is damaged."),
        ("CUST-00742", "I have not received my monitor and it is past the delivery date."),
        ("CUST-00158", "I requested a refund over a week ago and have not heard back."),
        # Invalid inputs
        ("", "Some issue description here."),
        ("CUST-00391", ""),
        ("CUST-00391", "hi"),
    ]

    for cid, issue in test_cases:
        result = create_support_ticket(cid, issue)
        print(f"\nInput : customer_id={cid!r}, issue={issue!r}")
        print(f"Output: {json.dumps(result, indent=2)}")
