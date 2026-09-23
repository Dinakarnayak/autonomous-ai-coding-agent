import pytest
from pydantic import ValidationError
from app.models import RunRequest


def test_request_defaults_to_no_publication():
    request = RunRequest(owner="octocat", repo="hello-world", issue_number=2)
    assert request.create_draft_pr is False
    assert request.base_branch is None


def test_rejects_invalid_issue_number():
    with pytest.raises(ValidationError):
        RunRequest(owner="octocat", repo="hello-world", issue_number=0)
