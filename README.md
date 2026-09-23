# Autonomous AI Coding Agent

A human-reviewed coding agent that turns a GitHub issue into a proposed patch, validates the patch in an isolated Docker container, and can open a draft pull request. It never merges or pushes without an explicit publish request.

## Current MVP

- FastAPI endpoint starts a run from `owner/repo` and issue number.
- LangGraph coordinates issue loading, planning, patch generation, isolated tests, and optional draft PR creation.
- GitHub access uses a fine-grained token; repository code runs in Docker with networking disabled.
- All runs are recorded in SQLite with their state and proposed diff.

## Quick start

1. Copy `.env.example` to `.env` and set `OPENAI_API_KEY`, `GITHUB_TOKEN`, and the optional OpenAI-compatible model settings.
2. Start Docker Desktop / Docker Engine.
3. Install and run:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

On Linux/macOS, activate with `source .venv/bin/activate`.

4. Start a run:

```powershell
Invoke-RestMethod -Method Post http://localhost:8000/runs `
  -ContentType 'application/json' `
  -Body '{"owner":"octocat","repo":"Hello-World","issue_number":1}'
```

Fetch status and the proposed patch at `GET /runs/{run_id}`. Set `create_draft_pr: true` in the request to publish a branch and draft PR after checks pass. The token needs Issues (read), Contents (read/write), and Pull requests (write) permissions. Restrict the token to repositories you trust.

## Configuration

`OPENAI_BASE_URL` may point at any OpenAI Chat Completions compatible endpoint. `SANDBOX_IMAGE` defaults to `python:3.12-slim`; `SANDBOX_TIMEOUT_SECONDS` caps execution time. Docker sandbox has no network and receives the checkout as its only mounted directory. Tests are run with `pytest -q` when a `tests/` directory exists, otherwise the workflow reports that no tests were found.

## API

- `GET /health` — liveness.
- `POST /runs` — body: `owner`, `repo`, `issue_number`, `base_branch` (optional), `create_draft_pr` (default false). Returns a run id immediately.
- `GET /runs/{run_id}` — run status, plan, summary, diff, and failure detail.

Runs execute in a background task. For production, replace SQLite/background tasks with PostgreSQL and a durable queue such as Redis + Celery/Arq, add authentication to the API, and store secrets in a secret manager.

## Safety boundaries

- Generated changes require successful `git apply --check` before applying.
- Tests execute in a Docker container with `--network none`, resource limits, and no Docker socket mount.
- A human must review the draft PR. This service does not merge PRs.
- Do not expose the API publicly without adding authentication and per-user repository authorization.

## Development

```bash
python -m pytest
```

The GitHub and LLM clients are separated into modules for straightforward mocking in future tests.
