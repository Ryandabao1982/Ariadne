<<<<<<< HEAD
# Ariadne: The Research Navigator

> An AI research partner that learns as you explore.

Ariadne is a super-agent designed to transform how you conduct research. It doesn't just answer questions; it builds a persistent, evolving knowledge base tailored to you. By accumulating knowledge and recognizing your unique research patterns, Ariadne helps you discover connections you never knew existed.

## ✨ Key Features

- **Intelligent Synthesis:** Get cited, comprehensive reports from multiple sources.
- **Persistent Memory:** Your entire research history is searchable and interconnected.
- **The Loom:** Visualize your knowledge as an interactive constellation map.
- **Adaptive Learning:** Ariadne learns your preferences for sources and styles to provide increasingly relevant results.
- **Collaborative Research:** Share and co-edit research with your team members.
- **Document Lifecycle:** Edit, version, and export your research reports in multiple formats.

## 🚀 Quick Start

1.  **Clone the repository**
    ```bash
    git clone https://github.com/your-org/ariadne.git
    cd ariadne
    ```

2.  **Set up your environment**
    ```bash
    # Backend setup
    cd backend
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    pip install -r requirements.txt

    # Frontend setup (in a new terminal)
    cd ../frontend
    npm install
    ```

3.  **Configure your environment variables**
    ```bash
    # Backend
    cp .env.example .env
    # Edit .env with your API keys for OpenAI, Pinecone, Neo4j, Auth0, etc.

    # Frontend
    cp .env.example .env.local
    # Configure Auth0/Clerk and API endpoints
    ```

4.  **Run the application**
    ```bash
    # Backend (in backend/ directory)
    uvicorn main:app --reload --port 8000

    # Frontend (in frontend/ directory)
    npm run dev -- --port 3000
    ```

## 📖 Documentation

- [Product Requirements Document (PRD)](docs/PRD.md)
- [Technical Architecture](docs/ARCHITECTURE.md)
- [Development Plan](docs/DEVELOPMENT_PLAN.md)
- [User Management Strategy](docs/USER_MANAGEMENT_STRATEGY.md)
- [Contributing Guidelines](CONTRIBUTING.md)

## 🏗️ Architecture

This project uses a microservices-oriented architecture centered around an Agent Orchestrator, a dual-database memory system (Vector + Graph), and a modern React frontend. See the [Architecture doc](docs/ARCHITECTURE.md) for details.

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md).

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
=======
# Ariadne
An AI research partner that learns as you explore.
>>>>>>> origin/main
