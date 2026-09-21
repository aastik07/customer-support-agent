"""
backend/tools/refund_status.py

Custom tool: check_refund_status
Looks up the refund status for a given order from data/orders.json
and returns a structured, agent-readable response.

Used by the Foundry Agent as a registered tool function.
Does not connect to Microsoft Foundry directly.
"""

import json
from pathlib import Path
from typing import Any

# ── Data source ───────────────────────────────────────────────────────────────

_DATA_PATH = Path(__file__).parent.parent.parent / "data" / "orders.json"

# Human-readable descriptions the agent can relay directly to the customer.
_REFUND_DESCRIPTIONS: dict[str, str] = {
    "None": (
        "No refund has been requested for this order. "
        "If you would like to request a refund, please let us know."
    ),
    "Refund Requested": (
        "A refund has been requested for this order and is currently under review. "
        "Our team typically processes refund requests within 2 business days."
    ),
    "Refunded": (
        "A refund has already been issued for this order. "
        "Please allow 3–5 business days for the funds to appear in your account, "
        "depending on your payment provider."
    ),
}


def _load_orders() -> list[dict[str, Any]]:
    """Load and return all orders from the JSON data file."""
    with _DATA_PATH.open(encoding="utf-8") as f:
        return json.load(f)


# ── Tool function ─────────────────────────────────────────────────────────────

def check_refund_status(order_id: str) -> dict[str, Any]:
    """
    Look up the refund status for a given order.

    Parameters
    ----------
    order_id : str
        The order identifier to look up (e.g. "NB-1063017").

    Returns
    -------
    dict
        On success:
            {
                "found": True,
                "order_id": str,
                "customer_name": str,
                "product": str,
                "order_status": str,
                "refund_status": str,
                "refund_description": str
            }

        On failure (order not found or bad input):
            {
                "found": False,
                "order_id": str,
                "error": str
            }
    """
    if not order_id or not isinstance(order_id, str):
        return {
            "found": False,
            "order_id": order_id,
            "error": "Invalid order ID provided. Please supply a valid order number.",
        }

    normalised_id = order_id.strip().upper()

    try:
        orders = _load_orders()
    except FileNotFoundError:
        return {
            "found": False,
            "order_id": order_id,
            "error": "Order data is temporarily unavailable. Please try again later.",
        }
    except json.JSONDecodeError:
        return {
            "found": False,
            "order_id": order_id,
            "error": "Order data could not be read. Please contact support.",
        }

    for order in orders:
        if order.get("order_id", "").upper() == normalised_id:
            refund_status = order["refund_status"]
            description = _REFUND_DESCRIPTIONS.get(
                refund_status,
                "The refund status for this order is unknown. Please contact support.",
            )
            return {
                "found": True,
                "order_id": order["order_id"],
                "customer_name": order["customer_name"],
                "product": order["product"],
                "order_status": order["status"],
                "refund_status": refund_status,
                "refund_description": description,
            }

    return {
        "found": False,
        "order_id": order_id,
        "error": (
            f"No order found with ID '{order_id}'. "
            "Please check the order number and try again."
        ),
    }


# ── Quick manual test ─────────────────────────────────────────────────────────

if __name__ == "__main__":
    test_cases = [
        "NB-1042873",   # Delivered      — refund_status: None
        "NB-1063017",   # Delivered      — refund_status: Refund Requested
        "NB-1034682",   # Delivered      — refund_status: Refunded
        "NB-1021337",   # Cancelled      — refund_status: Refunded
        "NB-9999999",   # not found
        "",             # invalid input
    ]

    for test_id in test_cases:
        result = check_refund_status(test_id)
        print(f"\nInput : {test_id!r}")
        print(f"Output: {json.dumps(result, indent=2)}")
