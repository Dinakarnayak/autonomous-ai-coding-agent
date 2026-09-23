import json
import sqlite3
from pathlib import Path
from app.config import get_settings


def _connect():
    path = Path(get_settings().database_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with _connect() as db:
        db.execute("""CREATE TABLE IF NOT EXISTS runs (
            id TEXT PRIMARY KEY, owner TEXT NOT NULL, repo TEXT NOT NULL,
            issue_number INTEGER NOT NULL, status TEXT NOT NULL,
            request_json TEXT NOT NULL, result_json TEXT NOT NULL DEFAULT '{}',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)""")


def create_run(run_id: str, request: dict):
    with _connect() as db:
        db.execute("INSERT INTO runs(id, owner, repo, issue_number, status, request_json) VALUES(?,?,?,?,?,?)",
                   (run_id, request["owner"], request["repo"], request["issue_number"], "queued", json.dumps(request)))


def update_run(run_id: str, status: str, **result):
    with _connect() as db:
        db.execute("UPDATE runs SET status=?, result_json=?, updated_at=CURRENT_TIMESTAMP WHERE id=?",
                   (status, json.dumps(result), run_id))


def get_run(run_id: str):
    with _connect() as db:
        row = db.execute("SELECT * FROM runs WHERE id=?", (run_id,)).fetchone()
    if not row:
        return None
    result = json.loads(row["result_json"])
    return {"id": row["id"], "owner": row["owner"], "repo": row["repo"],
            "issue_number": row["issue_number"], "status": row["status"], **result}
