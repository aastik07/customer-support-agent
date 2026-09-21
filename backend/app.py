"""
backend/app.py

FastAPI application entry point.

Endpoints
---------
GET  /health                  — liveness check (no auth)
POST /chat                    — send a message to the agent (no auth)
GET  /orders/{order_id}       — look up an order         [x-api-key required]
GET  /customers/{customer_id} — look up a customer       [x-api-key required]
GET  /refunds/{order_id}      — check refund status      [x-api-key required]
POST /tickets                 — create a support ticket  [x-api-key required]

Authentication (custom tool endpoints):
    Header:  x-api-key
    Value:   set CUSTOMER_SUPPORT_API_KEY in your .env file

Run locally:
    uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000

OpenAPI docs:
    http://localhost:8000/docs
    http://localhost:8000/openapi.json
"""

from __future__ import annotations

from fastapi import Depends, FastAPI, HTTPException, Request, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, Field

from backend.tools.order_status import check_order_status
from backend.tools.customer_info import get_customer_info
from backend.tools.refund_status import check_refund_status
from backend.tools.support_ticket import create_support_ticket

from backend.agent import AgentNotConfiguredError, get_agent_response
from backend.config import settings

# ── API-key security scheme ───────────────────────────────────────────────────
# This registers the x-api-key header in the OpenAPI schema so Microsoft
# Foundry's OpenAPI Tool importer picks it up automatically.

_api_key_header = APIKeyHeader(name="x-api-key", auto_error=False)


def _require_api_key(api_key: str | None = Security(_api_key_header)) -> str:
    """
    Dependency that validates the x-api-key header against the value stored
    in the CUSTOMER_SUPPORT_API_KEY environment variable.

    Raises HTTP 401 if the header is missing or the key does not match.
    Raises HTTP 503 if the server-side key has not been configured.
    """
    configured_key = settings.customer_support_api_key
    if not configured_key:
        raise HTTPException(
            status_code=503,
            detail=(
                "API key authentication is not configured on this server. "
                "Set CUSTOMER_SUPPORT_API_KEY in your .env file."
            ),
        )
    if not api_key or api_key != configured_key:
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API key. Provide a valid x-api-key header.",
        )
    return api_key


# ── Application ───────────────────────────────────────────────────────────────

app = FastAPI(
    title="NovaBuy Customer Support Agent",
    description=(
        "FastAPI backend for the NovaBuy AI customer support agent.\n\n"
        "**Custom tool endpoints** (`/orders`, `/customers`, `/refunds`, `/tickets`) "
        "are secured with an API key passed in the `x-api-key` request header. "
        "Microsoft Foundry connects to these endpoints via the OpenAPI 3.x "
        "specification served at `/openapi.json`.\n\n"
        "The `/health` and `/chat` endpoints do not require authentication."
    ),
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS ──────────────────────────────────────────────────────────────────────
# Allow the frontend (served from file:// or localhost) to call the API.
# Restrict origins in production.

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # tighten this when deploying
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "x-api-key"],
)

# ── Request / Response models ─────────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="The user's message to the support agent.",
        examples=["What is your return policy?"],
    )
    thread_id: str | None = Field(
        default=None,
        description=(
            "Optional conversation thread ID returned from a previous /chat call. "
            "Pass this back to maintain multi-turn context."
        ),
    )


class ChatResponse(BaseModel):
    reply: str = Field(..., description="The agent's response.")
    thread_id: str = Field(..., description="Thread ID to pass on the next request.")
    stub: bool = Field(
        default=False,
        description="True when the response is a stub (Foundry not yet connected).",
    )


class SupportTicketRequest(BaseModel):
    customer_id: str = Field(
        ...,
        min_length=1,
        description="Customer ID for the support ticket.",
        examples=["CUST-00391"],
    )
    issue: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Description of the customer's issue.",
        examples=["My order arrived damaged."],
    )


# ── System routes (no authentication) ────────────────────────────────────────

@app.get(
    "/health",
    tags=["System"],
    operation_id="health_check",
    summary="Liveness check",
)
def health_check():
    """
    Liveness check. Returns 200 OK when the server is running.
    Also reports whether Foundry credentials have been configured.
    """
    return {
        "status": "ok",
        "foundry_configured": settings.is_foundry_configured(),
    }


@app.post(
    "/chat",
    response_model=ChatResponse,
    tags=["Agent"],
    operation_id="chat",
    summary="Send a message to the support agent",
)
def chat(request: ChatRequest):
    """
    Send a message to the customer support agent and receive a reply.

    - If Microsoft Foundry is not yet configured, a stub response is returned.
    - Pass the returned `thread_id` back on subsequent requests to maintain
      conversation context across multiple turns.
    """
    try:
        result = get_agent_response(
            message=request.message,
            thread_id=request.thread_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except AgentNotConfiguredError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        # Do not expose internal error details to the client.
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred. Please try again later.",
        ) from exc

    return ChatResponse(**result)


# ── Custom Tool Routes (x-api-key required) ───────────────────────────────────
# All four routes below require the x-api-key header.
# FastAPI automatically adds the APIKeyHeader security scheme to the generated
# OpenAPI specification, which Microsoft Foundry reads when importing this API
# as an OpenAPI Tool.

@app.get(
    "/orders/{order_id}",
    tags=["Custom Tools"],
    operation_id="get_order_status",
    summary="Get the status of a customer order",
    dependencies=[Depends(_require_api_key)],
)
def order_status(order_id: str):
    """
    Look up the current status of a customer order by order ID.

    Returns order details including status, product, and expected delivery date.
    Returns 404 if the order ID is not found.
    """
    result = check_order_status(order_id)

    if not result.get("found"):
        raise HTTPException(status_code=404, detail=result)

    return result


@app.get(
    "/customers/{customer_id}",
    tags=["Custom Tools"],
    operation_id="get_customer_info",
    summary="Retrieve customer profile and order history",
    dependencies=[Depends(_require_api_key)],
)
def customer_info(customer_id: str):
    """
    Retrieve a customer's profile and full order history by customer ID.

    Returns the customer name, total orders, and a list of all orders.
    Returns 404 if the customer ID is not found.
    """
    result = get_customer_info(customer_id)

    if not result.get("found"):
        raise HTTPException(status_code=404, detail=result)

    return result


@app.get(
    "/refunds/{order_id}",
    tags=["Custom Tools"],
    operation_id="check_refund_status",
    summary="Check the refund status of an order",
    dependencies=[Depends(_require_api_key)],
)
def refund_status(order_id: str):
    """
    Look up the refund status for a given order ID.

    Returns refund status, description, and order details.
    Returns 404 if the order ID is not found.
    """
    result = check_refund_status(order_id)

    if not result.get("found"):
        raise HTTPException(status_code=404, detail=result)

    return result


@app.post(
    "/tickets",
    tags=["Custom Tools"],
    operation_id="create_support_ticket",
    summary="Create a customer support ticket",
    dependencies=[Depends(_require_api_key)],
)
def support_ticket(request: SupportTicketRequest):
    """
    Create a support ticket on behalf of a customer.

    Accepts a customer ID and a plain-text description of the issue.
    Returns a ticket ID, status, and expected response time.
    Returns 400 if the input is invalid.
    """
    result = create_support_ticket(
        request.customer_id,
        request.issue,
    )

    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result)

    return result


# ── Global error handler ──────────────────────────────────────────────────────

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred. Please try again later."},
    )
