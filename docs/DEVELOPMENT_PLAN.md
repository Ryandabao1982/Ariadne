# Technical Development Plan

## Phased Rollout

### Phase 0: Quality Foundation (Sprints -1 to 0)
**Goal:** Before writing a single line of feature code, we must build the automated quality assurance pipeline and the user management foundation. This is a prerequisite for all other work.

- **Sprint -2: The Public Experience**
  - [ ] Build the landing page with the "Public Research Playground"
  - [ ] Implement anonymous query rate limiting (by IP)
  - [ ] Create the "Share Public Tapestry" URL generation logic
  - [ ] Design the post-query "Sign Up" conversion modal

- **Sprint -1: User Management & Auth**
  - [ ] Set up Auth0/Clerk account and configure application.
  - [ ] Implement JWT middleware in FastAPI backend.
  - [ ] Create User, Subscription, and Session models in PostgreSQL.
  - [ ] Build Login/Signup flows in the frontend.
  - [ ] Implement Profile page UI.

- **Sprint 0: Testing Frameworks & Golden Dataset**
  - [ ] Set up `pytest` and `Jest` with coverage reporting.
  - [ ] Create the initial "Golden Dataset" of 10-15 queries.
  - [ ] Build the "Judge LLM" evaluation script.
  - [ ] Implement the first "Red Team" safety tests.

- **Sprint -0.5: Durable Workflows**
  - [ ] Evaluate and select a workflow orchestration engine (Temporal vs. Prefect).
  - [ ] Integrate the chosen engine into the `AriadneOrchestrator`.
  - [ ] Refactor the research process into a durable, resumable workflow.

### Phase 1: MVP - Core Research Loop (Sprints 1-4)
**Goal:** Deliver a functional agent that can research, synthesize, and store information in a vector database.

- **Sprint 1: Foundation (Weeks 1-2)**
  - [ ] Set up project structure (monorepo for backend/frontend).
  - [ ] Implement basic FastAPI backend structure.
  - [ ] Integrate LangChain orchestrator with a single LLM.
  - [ ] Create "Hello World" tool call.

- **Sprint 2: Tooling (Weeks 3-4)**
  - [ ] Implement `WebSearchTool` (Tavily/SerpApi).
  - [ ] Implement `DocumentIngestionTool` (URL, PDF).
  - [ ] Create robust error handling for tool failures.

- **Sprint 3: Memory Layer (Weeks 5-6)**
  - [ ] Set up Pinecone vector database.
  - [ ] Implement text chunking and embedding pipeline.
  - [ ] Create API endpoints for storing and querying chunks.
  - [ ] Connect orchestrator to Vector DB for context retrieval.

- **Sprint 4: UI & Synthesis (Weeks 7-8)**
  - [ ] Build basic React UI with a dialogue pane.
  - [ ] Implement `SynthesisTool` to generate final reports.
  - [ ] Connect frontend to backend via WebSocket for real-time updates.
  - [ ] End-to-end testing of the full MVP flow.

### Phase 2: Learning & Visualization (Sprints 5-8)
**Goal:** Introduce the Graph DB, feedback mechanisms, and The Loom visualization.

- **Sprint 5: Structured Memory (Weeks 9-10)**
  - [ ] Set up Neo4j graph database.
  - [ ] Implement schema for User, Topic, Source, etc.
  - [ ] Create services to write/read nodes and relationships.
  - [ ] Update orchestrator to populate the Graph DB.

- **Sprint 6: Feedback & Logging (Weeks 11-12)**
  - [ ] Set up PostgreSQL operational database.
  - [ ] Implement logging for all user interactions and agent actions.
  - [ ] Add UI feedback controls (👍/👎, 🧵 button).
  - [ ] Create backend endpoints to receive this feedback.

- **Sprint 7: First Learning Model (Weeks 13-14)**
  - [ ] Develop the Source Preference Re-ranker model.
  - [ ] Train it on the collected feedback data.
  - [ ] Integrate the model into the search pipeline.

- **Sprint 8: The Loom UI (Weeks 15-16)**
  - [ ] Implement the visual knowledge graph component (using D3.js or a similar library).
  - [ ] Connect the frontend to the Neo4j API.
  - [ ] Implement interactive features (zoom, pan, click-to-query).

### Phase 3: Autonomy & Polish (Sprints 9+)
**Goal:** Implement proactive features and refine the user experience.
- [ ] Proactive research and alert system.
- [ ] Advanced query intent refinement.
- [ ] UI/UX polish and performance optimization.
- [ ] User testing and feedback iteration.

### Phase 4: Autonomy & Collaboration (Sprints 13-16)
**Goal:** Implement The Muse, confidence scoring, and shared Looms.

- **Sprint 13: The Muse Engine**
  - [ ] Design the background job architecture for proactive monitoring.
  - [ ] Implement the initial logic for monitoring trusted sources.
  - [ ] Create the notification system for proactive discoveries.

- **Sprint 14: Confidence & Contradiction**
  - [ ] Develop the "Confidence Layer" module.
  - [ ] Integrate source cross-referencing into the synthesis pipeline.
  - [ ] Add UI elements for confidence indicators and contradiction flags.

- **Sprint 15: Collaborative Looms - Backend**
  - [ ] Update Graph DB schema for permissions and shared nodes.
  - [ ] Implement API endpoints for creating, managing, and inviting to shared Looms.
  - [ ] Add real-time update mechanism (e.g., WebSockets).

- **Sprint 16: Collaborative Looms - Frontend**
  - [ ] Build UI for creating and managing shared Looms.
  - [ ] Implement real-time UI updates for collaborative sessions.
  - [ ] End-to-end testing of the full collaboration flow.

### Phase 5: Platform & Ecosystem (Sprints 17+)
**Goal:** Build the foundations for the Ariadne Marketplace and offline capabilities.

- **Sprint 17: Marketplace SDK & Backend**
  - [ ] Define the final Plugin SDK based on `interfaces.py`.
  - [ ] Create a sandboxed execution environment for third-party plugins.
  - [ ] Build the backend for the marketplace (listing, submission, versioning).

- **Sprint 18: Offline-First Architecture**
  - [ ] Research and select local vector/graph DB solutions.
  - [ ] Design the data synchronization protocol between client and server.
  - [ ] Implement the local-first caching layer in the frontend.

### Phase 6: The Tapestry Editor & Lifecycle (Sprints 21-24)
**Goal:** Implement the full, interactive lifecycle for compiled knowledge.

- **Sprint 21: Backend Data Model & API**
  - [ ] Update Graph DB schema for `Tapestry` nodes and relationships.
  - [ ] Implement the `Tapestry Service` with full CRUD and versioning logic.
  - [ ] Create API endpoints for fetching, saving, and versioning Tapestries.

- **Sprint 22: Frontend Viewer & Basic Editor**
  - [ ] Build the Tapestry Workspace modal and its toolbar.
  - [ ] Implement the "View Mode" with inline citations.
  - [ ] Integrate a rich-text editor library (e.g., TipTap, Slate.js).

- **Sprint 23: AI Assist & Versioning**
  - [ ] Implement the "AI Assist" menu and its backend logic.
  - [ ] Build the "Version History" sidebar and its functionality.
  - [ ] Connect the "Save" action to the versioning API.

- **Sprint 24: Export Engine & Collaboration**
  - [ ] Build the `Export Engine` microservice.
  - [ ] Implement the real-time co-editing backend using WebSockets.
  - [ ] Add the sharing and permission logic to the UI and backend.

## Updated Tech Stack Summary
| Layer | Technology |
|---|---|
| **Backend** | Python, FastAPI, Pydantic |
| **Agent Framework** | LangChain |
| **LLM** | OpenAI GPT-4o / Anthropic Claude 3 Opus |
| **Vector DB** | Pinecone (Cloud), `Omnivore` (Local) |
| **Graph DB** | Neo4j (Cloud), `ONgDB` (Local) |
| **Operational DB** | PostgreSQL |
| **Frontend** | React / Next.js, TypeScript, Tailwind CSS, Webpack Module Federation |
| **Deployment** | Docker, Kubernetes, AWS/GCP |
| **Real-time** | WebSockets |
| **Local LLMs** | `llama.cpp` or `Ollama` integration |
