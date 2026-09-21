"""
backend/tools/customer_info.py

Custom tool: get_customer_info
Derives customer profile and order history from data/orders.json.
No separate customers table is required — all data is aggregated
from the order records at call time.

Used by the Foundry Agent as a registered tool function.
Does not connect to Microsoft Foundry directly.
"""

import json
from pathlib import Path
from typing import Any

# ── Data source ───────────────────────────────────────────────────────────────

_DATA_PATH = Path(__file__).parent.parent.parent / "data" / "orders.json"


def _load_orders() -> list[dict[str, Any]]:
    """Load and return all orders from the JSON data file."""
    with _DATA_PATH.open(encoding="utf-8") as f:
        return json.load(f)


# ── Tool function ─────────────────────────────────────────────────────────────

def get_customer_info(customer_id: str) -> dict[str, Any]:
    """
    Retrieve a customer's profile and full order history by customer ID.

    Customer data is derived from order records — there is no separate
    customer database. The function aggregates all orders belonging to
    the given customer_id and builds a structured profile from them.

    Parameters
    ----------
    customer_id : str
        The customer identifier to look up (e.g. "CUST-00391").

    Returns
    -------
    dict
        On success:
            {
                "found": True,
                "customer_id": str,
                "customer_name": str,
                "total_orders": int,
                "orders": [
                    {
                        "order_id": str,
                        "product": str,
                        "status": str,
                        "order_date": str,
                        "expected_delivery": str,
                        "refund_status": str
                    },
                    ...
                ]
            }

        On failure (customer not found):
            {
                "found": False,
                "customer_id": str,
                "error": str
            }
    """
    if not customer_id or not isinstance(customer_id, str):
        return {
            "found": False,
            "customer_id": customer_id,
            "error": "Invalid customer ID provided. Please supply a valid customer ID.",
        }

    normalised_id = customer_id.strip().upper()

    try:
        orders = _load_orders()
    except FileNotFoundError:
        return {
            "found": False,
            "customer_id": customer_id,
            "error": "Customer data is temporarily unavailable. Please try again later.",
        }
    except json.JSONDecodeError:
        return {
            "found": False,
            "customer_id": customer_id,
            "error": "Customer data could not be read. Please contact support.",
        }

    # Collect all orders belonging to this customer.
    customer_name: str | None = None
    customer_orders: list[dict[str, Any]] = []

    for order in orders:
        if order.get("customer_id", "").upper() == normalised_id:
            customer_name = order["customer_name"]
            customer_orders.append(
                {
                    "order_id": order["order_id"],
                    "product": order["product"],
                    "status": order["status"],
                    "order_date": order["order_date"],
                    "expected_delivery": order["expected_delivery"],
                    "refund_status": order["refund_status"],
                }
            )

    if not customer_orders:
        return {
            "found": False,
            "customer_id": customer_id,
            "error": (
                f"No customer found with ID '{customer_id}'. "
                "Please check the customer ID and try again."
            ),
        }

    return {
        "found": True,
        "customer_id": customer_id,
        "customer_name": customer_name,
        "total_orders": len(customer_orders),
        "orders": customer_orders,
    }


# ── Quick manual test ─────────────────────────────────────────────────────────

if __name__ == "__main__":
    test_cases = [
        "CUST-00391",   # valid — 1 order, Delivered
        "CUST-00158",   # valid — 1 order, Refund Requested
        "CUST-00995",   # valid — 1 order, Delayed
        "CUST-99999",   # invalid — not found
        "",             # invalid — empty string
    ]

    for test_id in test_cases:
        result = get_customer_info(test_id)
        print(f"\nInput : {test_id!r}")
        print(f"Output: {json.dumps(result, indent=2)}")
