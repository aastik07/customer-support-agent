# Customer Support Agent — Project Context

## Project Goal

Build an intelligent Customer Support Agent as a solo project that can:

- Answer customer questions accurately using a curated knowledge base (RAG).
- Call custom tools to look up live data (e.g., order status, refund eligibility).
- Maintain a natural, multi-turn conversation through a simple web UI.
- Demonstrate a production-style AI agent architecture using Microsoft Foundry.

The agent acts as a first-line support assistant — grounding its answers in trusted
documents and escalating or fetching real data via tools when needed.

---

## Technology Stack

| Layer            | Technology                                      |
|------------------|-------------------------------------------------|
| AI Platform      | Microsoft Foundry                               |
| Agent Runtime    | Microsoft Foundry Agent Service                 |
| RAG / Search     | Foundry IQ + Azure AI Search                   |
| Backend          | Python 3.11+, FastAPI                           |
| Frontend         | HTML, CSS, JavaScript (vanilla)                 |
| Version Control  | GitHub                                          |
| Config / Secrets | `.env` file (never committed)                   |

---

## Agent Responsibilities

The **Foundry Agent** is the core intelligence of the system. It is responsible for:

- Receiving user messages from the FastAPI backend.
- Deciding whether to answer directly, query the knowledge base (RAG), or invoke a custom tool.
- Maintaining conversation context across multiple turns.
- Generating grounded, helpful responses based on retrieved documents and tool outputs.
- Following a system prompt that defines its persona, tone, and constraints.

---

## Foundry IQ Responsibilities

**Foundry IQ** powers the RAG (Retrieval-Augmented Generation) pipeline. It is responsible for:

- Indexing knowledge base documents stored in the `knowledge/` directory.
- Converting user queries into vector embeddings and retrieving the most relevant document chunks.
- Returning ranked, relevant passages to the agent so it can cite and ground its answers.
- Being the single source of truth for product information, policies, and FAQs.

---

## Custom Tool Responsibilities

Custom tools extend the agent beyond static knowledge. They are Python functions
registered with the Foundry Agent that it can invoke during a conversation.

Each tool must:
- Accept a well-defined set of parameters (validated via JSON schema).
- Return a structured response the agent can parse and summarize.
- Handle errors gracefully and return a clear error message on failure.
- Never expose credentials or internal implementation details to the agent or user.

---

## Frontend / Backend Architecture

```
User (Browser)
     │
     │  HTTP POST /chat  { "message": "..." }
     ▼
┌─────────────────────────────┐
│       FastAPI Backend       │  backend/
│                             │
│  • Receives user message    │
│  • Forwards to Foundry Agent│
│  • Streams / returns reply  │
└────────────┬────────────────┘
             │  Foundry Agent SDK
             ▼
┌─────────────────────────────┐
│    Microsoft Foundry Agent  │
│                             │
│  • Reads system prompt      │
│  • Queries Foundry IQ (RAG) │
│  • Calls custom tools       │
│  • Returns final response   │
└─────────────────────────────┘
```

- The **frontend** is a single HTML page that sends messages to the backend and renders replies.
- The **backend** is a stateless FastAPI app; session/thread state is managed by the Foundry Agent.
- The backend is the only component that holds credentials (via `.env`).

---

## Four Custom Tools

### 1. `check_order_status`
- **Purpose**: Look up the current status of a customer's order.
- **Input**: `order_id` (string)
- **Output**: Order status, estimated delivery date, refund state.
- **Location**: `backend/tools/order_status.py`

### 2. `get_customer_info`
- **Purpose**: Retrieve a customer profile and order history.
- **Input**: `customer_id` (string)
- **Output**: Customer name, total orders, and order list.
- **Location**: `backend/tools/customer_info.py`

### 3. `check_refund_status`
- **Purpose**: Check the refund status of a specific order.
- **Input**: `order_id` (string)
- **Output**: Refund state and human-readable description.
- **Location**: `backend/tools/refund_status.py`

### 4. `create_support_ticket`
- **Purpose**: Create a support ticket when the agent cannot resolve the issue.
- **Input**: `customer_id` (string), `issue` (string)
- **Output**: Ticket ID, status, SLA, confirmation message.
- **Location**: `backend/tools/support_ticket.py`

---

## Five Planned Knowledge Documents

| # | File (knowledge/)              | Contents                                                         |
|---|-------------------------------|------------------------------------------------------------------|
| 1 | `faq.md`                      | Top 30 frequently asked customer questions and answers           |
| 2 | `return_refund_policy.md`     | Full return and refund policy, eligibility rules, timelines      |
| 3 | `shipping_policy.md`          | Shipping methods, delivery estimates, international orders       |
| 4 | `product_catalog_overview.md` | High-level product categories, features, and compatibility notes |
| 5 | `contact_escalation_guide.md` | When and how to escalate, department contacts, SLA expectations  |

---

## Solo Developer Responsibilities

This is a solo project. All areas of development are owned and integrated by a single developer.

| Area                  | Responsibility                                                                 |
|-----------------------|--------------------------------------------------------------------------------|
| Microsoft Foundry     | Provision and configure the Foundry workspace, models, and connections         |
| Foundry Agent         | Define the agent, system prompt, tool registrations, and conversation logic    |
| Foundry IQ / RAG      | Set up the knowledge index, manage documents, tune retrieval                   |
| Custom Tools          | Implement and test all Python tool functions registered with the agent         |
| FastAPI Backend       | Build and maintain all API routes, middleware, and credential handling         |
| Frontend              | Develop the single-page chat UI and integrate it with the backend              |
| Testing               | Write and run unit tests, integration tests, and end-to-end validation         |
| Documentation         | Keep all docs, comments, and this file accurate and up to date                 |
| GitHub                | Manage the repository, commits, branching, and version history                 |

---

## Project Rules

These rules apply at all times.

1. **Never expose secrets.** API keys, passwords, and tokens must never appear in code or commits.
2. **Never put Azure credentials in GitHub.** Use `.env` locally; use GitHub Secrets for CI/CD only.
3. **Never modify unrelated files.** Each task should touch only the files it needs to change.
4. **Do not rewrite existing files unless explicitly instructed.** Prefer targeted edits.
5. **Keep implementations simple.** Choose the straightforward solution over the clever one.
6. **Prefer small changes.** Incremental commits are easier to review and safer to merge.
7. **Do not create unnecessary Azure resources.** Every resource costs money and adds complexity.
8. **Do not change the architecture without good reason.** Think through structural changes carefully before implementing them.
