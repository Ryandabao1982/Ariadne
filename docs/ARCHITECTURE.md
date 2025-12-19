# Technical Architecture

## Overview
The Ariadne system is composed of four primary layers: Agent Orchestration, Tooling, Knowledge & Memory, and a Learning Module.

## 1. Agent Orchestration Core
- **Tech:** LangChain, GPT-4o
- **Responsibility:** The central brain. It plans tasks, selects tools, and manages the conversation flow.

## 2. Tooling & Execution Layer
- **Tech:** Python, Tavily API, PyPDF2
- **Responsibility:** A set of modular tools for performing actions (search, fetch, parse).

## 3. Knowledge & Memory Layer (The Single Source of Truth)
We have evolved from a "Dual-Memory" system to a unified **GraphRAG** architecture to eliminate synchronization errors and entity resolution ambiguity.

- **Technology:** **Neo4j** with its native vector search capabilities.
- **Schema:** The graph schema remains, but we will now store the text chunk embedding directly as a vector property on the node that represents that chunk of information.

### Node Example (Updated)
```cypher
(:Chunk {
  chunkId: 'chunk_abc123xyz',
  text: "...the mycelium binds the agricultural waste...",
  embedding: [0.01, -0.04, ..., 0.98], // The embedding vector
  sourceUri: 'https://arxiv.org/abs/2310.12345'
})
```

**How it Works:**
1.  **Ingestion:** When a document is processed, it's chunked, and each chunk is turned into a `Chunk` node in Neo4j.
2.  **Embedding:** The text is converted to an embedding and stored on that same node.
3.  **Relationships:** The `Chunk` node is then linked to higher-level nodes like `(:Source)` and `(:Topic)`.
4.  **Querying:** A user's query is also embedded. We then perform a single, unified vector similarity search *within the graph*, which can simultaneously find semantically similar chunks *and* traverse their relationships to other topics and sources in one atomic operation.

This eliminates the "Dual-Memory Synchronization Trap" by making the graph the single, authoritative source of all knowledge.

## 4. Learning & Adaptation Module
- **Tech:** Python, Scikit-learn, Pandas
- **Responsibility:** Analyzes interaction data from the operational DB to build models for personalization.

## 5. User Management & Authentication Layer
- **Tech:** Auth0/Clerk, FastAPI, PostgreSQL.
- **Responsibility:** Handles user authentication, authorization, profiles, session management, and subscription status. All API endpoints for user-related actions will be in a dedicated `api/v1/users/` path.

## 6. New Architectural Components

### The Muse (Proactive Discovery Engine)
- **Tech:** Python, Celery (for background tasks), Redis (for task queue).
- **Responsibility:** A background service that monitors user graphs and external data sources to proactively suggest new research avenues and discoveries.

### Confidence & Contradiction Layer
- **Tech:** Python, a smaller, faster LLM (e.g., `gpt-3.5-turbo`), rule-based systems.
- **Responsibility:** A post-processing step that validates the synthesized report against source evidence, assigns confidence scores, and flags contradictions.

### Real-time Collaboration Service
- **Tech:** WebSockets, Redis Pub/Sub.
- **Responsibility:** Manages real-time updates for Shared Looms, broadcasting changes to all connected clients in a collaborative session.

### Local Client & Sync Service
- **Tech:** Electron (for desktop app), ` IndexedDB`/`op-sqlite` (for local storage), `llama.cpp`.
- **Responsibility:** The frontend application itself, which maintains a local copy of the user's knowledge graph and syncs with the backend when online. It can also execute simple tasks using local LLMs.

### Event Deduplication Layer
- **Tech:** RabbitMQ or Kafka with a deduplication window.
- **Responsibility:** All write operations to the Graph DB that originate from a shared context (e.g., Shared Looms, co-editing Tapestries) will be placed into a message queue. The queue processor will buffer events for a short period (e.g., 5 seconds) to collapse duplicate or conflicting events into a single, atomic update.

## 7. Frontend Architecture: Cell-Based Design
The frontend is not a monolith but a collection of independently deployable "cells" orchestrated by a lightweight shell application.
- **Shell App:** Handles routing, authentication, and lazy-loads cells.
- **Cells:** `DialogueCell`, `LoomCell`, `SettingsCell`, `MarketplaceCell`.
- **Communication:** Cells communicate via a shared event bus or a global state management library.

## 8. Data Models

### Graph DB Schema (Updated)

#### Nodes
- **(:User {userId, name, email, created_at})**
- **(:Topic {name, canonical_name, last_researched, research_count})**
- **(:Source {sourceId, uri, title, type, domain, trust_score, published_at})**
- **(:Author {authorId, name, affiliation, h_index})**
- **(:Insight {insightId, summary, importance_score, created_at})**
- **(:Tapestry {tapestryId, title, content, createdAt, version, sourceSnapshot})**

#### Relationships
- `(User)-[:RESEARCHED {timestamp, rating, query}]->(Topic)`
- `(User)-[:PREFERS {strength, context}]->(Source)`
- `(User)-[:HAS_STYLE]->(:Style {type, description})`
- `(Topic)-[:RELATED_TO {strength}]->(Topic)`
- `(Topic)-[:HAS_KEY_SOURCE]->(Source)`
- `(Source)-[:AUTHORED_BY]->(Author)`
- `(Source)-[:CITES]->(Source)`
- `(Insight)-[:DERIVED_FROM {confidence}]->(Source)`
- `(User)-[:FLAGGED_AS_KEY]->(Insight)`
- `(:User)-[:AUTHORED]->(:Tapestry)`
- `(:Tapestry {version: 3})-[:PREVIOUS_VERSION]->(:Tapestry {version: 2})`
- `(:Tapestry)-[:DERIVED_FROM]->(:Topic)`

## 9. Technology Stack Summary
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
