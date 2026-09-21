"""
backend/tools/order_status.py

Custom tool: check_order_status
Reads fictional order data from data/orders.json and returns
structured order information for a given order_id.

Used by the Foundry Agent as a registered tool function.
Does not connect to Microsoft Foundry directly — the agent
calls this function and receives its return value.
"""

import json
from pathlib import Path
from typing import Any

# ── Data source ───────────────────────────────────────────────────────────────

# Resolve path relative to this file so it works regardless of where
# the backend is launched from.
_DATA_PATH = Path(__file__).parent.parent.parent / "data" / "orders.json"


def _load_orders() -> list[dict[str, Any]]:
    """Load and return all orders from the JSON data file."""
    with _DATA_PATH.open(encoding="utf-8") as f:
        return json.load(f)


# ── Tool function ─────────────────────────────────────────────────────────────

def check_order_status(order_id: str) -> dict[str, Any]:
    """
    Look up the current status of a customer order by order ID.

    Parameters
    ----------
    order_id : str
        The order identifier to look up (e.g. "NB-1042873").

    Returns
    -------
    dict
        On success:
            {
                "found": True,
                "order_id": str,
                "customer_name": str,
                "product": str,
                "status": str,
                "order_date": str,
                "expected_delivery": str,
                "refund_status": str
            }

        On failure (order not found):
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
            return {
                "found": True,
                "order_id": order["order_id"],
                "customer_name": order["customer_name"],
                "product": order["product"],
                "status": order["status"],
                "order_date": order["order_date"],
                "expected_delivery": order["expected_delivery"],
                "refund_status": order["refund_status"],
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
        "NB-1042873",   # valid — Delivered
        "NB-1058294",   # valid — In Transit
        "NB-1095768",   # valid — Delayed
        "NB-9999999",   # invalid — not found
        "",             # invalid — empty string
    ]

    for test_id in test_cases:
        result = check_order_status(test_id)
        print(f"\nInput : {test_id!r}")
        print(f"Output: {json.dumps(result, indent=2)}")
