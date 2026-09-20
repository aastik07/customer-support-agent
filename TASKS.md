# TASKS — Customer Support Agent

> **Legend**: `[ ]` To Do · `[/]` In Progress · `[x]` Done

---

## 1. GitHub

- [ ] Create the GitHub repository under the team organisation/account
- [ ] Add all four team members as collaborators
- [ ] Define branching strategy (`main`, `dev`, feature branches)
- [ ] Write branch protection rules for `main` (require PR + review)
- [ ] Add GitHub Secrets for CI/CD environment variables
- [ ] Create issue labels: `backend`, `frontend`, `rag`, `tools`, `docs`, `bug`
- [ ] Open tracking issues for each milestone below

---

## 2. Azure

- [ ] Create an Azure account / confirm student subscription is active
- [ ] Create a Resource Group for the project
- [ ] Set correct region for all resources (keep consistent)
- [ ] Confirm billing alerts are set to avoid unexpected charges
- [ ] Record all resource names in `docs/azure_resources.md` (no secrets)

---

## 3. Microsoft Foundry

- [ ] Provision a Microsoft Foundry project inside the Resource Group
- [ ] Note the Foundry endpoint URL in `.env.example`
- [ ] Create a Foundry Agent and record the Agent ID
- [ ] Write the agent system prompt (persona, tone, constraints)
- [ ] Configure the agent model (e.g., `gpt-4o`)
- [ ] Verify the agent responds correctly via the Foundry playground

---

## 4. Foundry IQ

- [ ] Enable Foundry IQ on the Foundry project
- [ ] Provision an Azure AI Search index for the knowledge base
- [ ] Connect the search index to the Foundry Agent
- [ ] Prepare and clean the five knowledge documents (`knowledge/`)
- [ ] Upload and index all five documents
- [ ] Test retrieval with at least five sample queries
- [ ] Tune chunking and top-K settings for best answer quality
- [ ] Document the index name and endpoint in `.env.example`

---

## 5. Custom Tools

- [ ] Design the JSON schema for all four tools (name, description, parameters, return type)
- [ ] Implement `get_order_status` in `backend/tools/order_status.py`
- [ ] Implement `check_refund_eligibility` in `backend/tools/refund_eligibility.py`
- [ ] Implement `get_product_info` in `backend/tools/product_info.py`
- [ ] Implement `create_support_ticket` in `backend/tools/create_ticket.py`
- [ ] Register all four tools with the Foundry Agent
- [ ] Test each tool in isolation with mock inputs
- [ ] Test each tool end-to-end through the agent in conversation

---

## 6. Backend

- [ ] Scaffold the FastAPI application in `backend/`
- [ ] Set up environment variable loading from `.env`
- [ ] Implement `POST /chat` endpoint (receive message, forward to agent, return reply)
- [ ] Integrate the Microsoft Foundry Agent SDK into the endpoint
- [ ] Add CORS middleware (allow frontend origin)
- [ ] Add basic input validation (empty message, max length)
- [ ] Add error handling and meaningful HTTP error responses
- [ ] Add a `GET /health` endpoint for liveness checks
- [ ] Test the API manually with a REST client (e.g., curl or Postman)

---

## 7. Frontend

- [ ] Create `frontend/index.html` with the chat UI layout
- [ ] Style the chat window, message bubbles, and input bar in `frontend/style.css`
- [ ] Implement `frontend/app.js` to send messages to `POST /chat`
- [ ] Display user messages and agent replies in the chat window
- [ ] Show a loading indicator while waiting for the agent response
- [ ] Handle and display error messages gracefully
- [ ] Make the UI responsive for desktop and mobile screen sizes
- [ ] Test the UI in Chrome, Firefox, and Edge

---

## 8. Integration

- [ ] Connect the frontend to the running FastAPI backend
- [ ] Verify a full round-trip: user message → backend → Foundry Agent → reply → UI
- [ ] Verify RAG is triggered: ask a question answered only in the knowledge base
- [ ] Verify tool calls are triggered: ask about order status, refunds, etc.
- [ ] Confirm no secrets appear in browser network requests or console logs
- [ ] Test multi-turn conversation (agent remembers context across messages)

---

## 9. Testing

- [ ] Write unit tests for each custom tool in `tests/`
- [ ] Write unit tests for the `/chat` and `/health` endpoints
- [ ] Write an integration test for a full chat round-trip (mocked agent)
- [ ] Run all tests and confirm they pass
- [ ] Measure and document test coverage
- [ ] Fix any bugs found during testing

---

## 10. Documentation

- [ ] Write `docs/setup_guide.md` — local environment setup instructions
- [ ] Write `docs/azure_resources.md` — list of all Azure resources (no secrets)
- [ ] Write `docs/agent_prompt.md` — current system prompt and rationale
- [ ] Write `docs/tools_reference.md` — schema and usage for each custom tool
- [ ] Write `docs/knowledge_base.md` — list of indexed documents and update process
- [ ] Update `README.md` with project overview, quickstart, and team info
- [ ] Review all docs for accuracy before the demo

---

## 11. Final Demo

- [ ] Deploy or run the full system locally in a stable state
- [ ] Prepare a 5-minute demo script covering: greeting → FAQ → tool call → escalation
- [ ] Rehearse the demo as a team at least once
- [ ] Prepare slides with architecture diagram and tech stack
- [ ] Record a backup video demo in case of live connectivity issues
- [ ] Submit all deliverables (code, docs, presentation) to the course portal
