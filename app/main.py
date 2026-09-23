import asyncio
from contextlib import asynccontextmanager
from uuid import uuid4
from fastapi import FastAPI, HTTPException
from app.models import RunRequest
from app import store
from app.agents.workflow import run_agent


@asynccontextmanager
async def lifespan(app: FastAPI):
    store.init_db()
    yield


app = FastAPI(title="Autonomous AI Coding Agent", version="0.1.0", lifespan=lifespan)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/runs", status_code=202)
async def create_run(request: RunRequest):
    run_id = str(uuid4())
    payload = request.model_dump()
    store.create_run(run_id, payload)
    asyncio.create_task(_execute(run_id, payload))
    return {"id": run_id, "status": "queued", "status_url": f"/runs/{run_id}"}


async def _execute(run_id: str, payload: dict):
    store.update_run(run_id, "running")
    try:
        result = await asyncio.to_thread(run_agent, payload)
        store.update_run(run_id, "completed", plan=result.get("plan"), summary=result.get("summary"),
                         diff=result.get("diff"), pull_request_url=result.get("pull_request_url"))
    except Exception as exc:
        store.update_run(run_id, "failed", error=f"{type(exc).__name__}: {exc}")


@app.get("/runs/{run_id}")
def get_run(run_id: str):
    result = store.get_run(run_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Run not found")
    return result
