<!-- Copilot instructions customized for the Ariadne repo. Keep this concise and update as the codebase evolves. -->
# Copilot Instructions — Ariadne (backend-first)

Purpose
- Help AI coding agents (and humans) become productive quickly by highlighting the repo's structure, run/test commands, and key integration points.

Quick repository facts (discovered)
- Backend is Python-based: see `backend/pyproject.toml` (FastAPI, Uvicorn, LangChain, Neo4j, Temporal, Alembic, Redis).
- Tests live under `tests/` and `pyproject.toml` declares `pytest` options and coverage thresholds.
- High-level roadmap and priorities are in `IMPLEMENTATION_TODO.md` and developer-facing guidance in `README.md`.

What to read first
- `backend/pyproject.toml` — dependency list, dev tools (black, mypy, pre-commit), and `pytest` settings.
- `README.md` — quickstart, expected dev environment and `uvicorn` run example.
- `IMPLEMENTATION_TODO.md` — product roadmap and feature phases (useful for aligning changes to priorities).
- `backend/core/interfaces.py` — core plugin/tool/orchestrator interfaces (key design points to follow when adding tools or models).

Big-picture architecture notes (from source)
- Orchestrator-First: core components center around an Orchestrator, ContextProviders, Tools, and Learning models (see `backend/core/interfaces.py`). When implementing features, prefer placing code in `core/` services or new subpackages that match those abstractions.
- Dual memory & integrations: dependencies show a Vector/Graph memory approach (Neo4j) plus Temporal for orchestration and Redis for caching/rate-limiting — changes touching memory, workflows, or tool integrations will need attention to these systems.
- Migrations & DB: Alembic + SQLAlchemy + asyncpg are present — database schema changes should use Alembic migrations.

Developer workflows (concrete)
- Create a Python venv and install using the Python packaging tools in `backend`:

  # POSIX
  cd backend
  python -m venv .venv
  source .venv/bin/activate
  pip install -e .

  # Windows (PowerShell)
  cd backend
  python -m venv .venv
  .\.venv\Scripts\Activate.ps1
  pip install -e .

- Run the backend locally (README example):

  uvicorn main:app --reload --port 8000

- Tests & coverage (pyproject configured):

  pytest

  # Coverage and reports are configured via `pyproject.toml` (`--cov=core`, HTML and XML outputs)

Project-specific conventions
- Layering: follow the `handlers → services → repositories` pattern. New features that expose APIs should add HTTP handlers (FastAPI routers) and keep business logic in `core/` modules.
- Plugin/tool model: implement new tools by conforming to `ToolInterface` in `backend/core/interfaces.py` and register them via the repository's registry pattern (see `backend/core/registry.py`).
- Type & linting: repo expects `black` formatting and `mypy` static typing with `disallow_untyped_defs`. Add type hints for public functions/methods.

Integration points & external dependencies
- Check `backend/pyproject.toml` for runtime dependencies: `neo4j`, `temporalio`, `redis`, `opentelemetry-*`, `langchain`, and LLM SDKs. Changes that touch these require local env variables (API keys) and could need dockerized services or cloud accounts to fully test.
- Database migrations: use Alembic for schema changes. Look for `alembic/` when adding migrations.

When editing code
- Respect `core` interfaces: use `ToolInterface`, `OrchestratorInterface`, and `ContextProviderInterface` as contracts.
- Add tests under `tests/` matching `unit` / `integration` markers declared in `pyproject.toml`.
- Run `black` and `mypy` locally (dev extras include these tools).

Files to inspect for examples
- `backend/pyproject.toml` — dependency and test config
- `backend/core/interfaces.py` — plugin + orchestrator contracts
- `backend/core/registry.py` — registry pattern for tools/plugins
- `IMPLEMENTATION_TODO.md` — roadmap and prioritized features
- `README.md` — quickstart, run commands, and architecture links

Next steps for me
- If you want, I can re-scan a specific backend subfolder (e.g., `backend/app`, `backend/api`) and expand examples (router names, entrypoints, common helper functions).

Feedback
- Tell me which area you'd like richer guidance for (tests, infra, adding a new tool, or CI). I'll re-run discovery and update this file with concrete code snippets and file links.
