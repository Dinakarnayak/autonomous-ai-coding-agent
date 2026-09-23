from typing import Literal
from pydantic import BaseModel, Field


class RunRequest(BaseModel):
    owner: str = Field(pattern=r"^[A-Za-z0-9_.-]{1,39}$")
    repo: str = Field(pattern=r"^[A-Za-z0-9_.-]{1,100}$")
    issue_number: int = Field(gt=0)
    base_branch: str | None = None
    create_draft_pr: bool = False


class RunRecord(BaseModel):
    id: str
    owner: str
    repo: str
    issue_number: int
    status: Literal["queued", "running", "completed", "failed"]
    plan: str | None = None
    summary: str | None = None
    diff: str | None = None
    pull_request_url: str | None = None
    error: str | None = None
