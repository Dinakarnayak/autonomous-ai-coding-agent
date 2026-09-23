import httpx
from app.config import get_settings


class GitHubClient:
    def __init__(self):
        token = get_settings().github_token
        if not token:
            raise RuntimeError("GITHUB_TOKEN is required")
        self.client = httpx.Client(
            base_url="https://api.github.com",
            headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json",
                     "X-GitHub-Api-Version": "2022-11-28"}, timeout=30)

    def request(self, method, path, **kwargs):
        response = self.client.request(method, path, **kwargs)
        response.raise_for_status()
        return response.json() if response.content else None

    def issue(self, owner, repo, number):
        return self.request("GET", f"/repos/{owner}/{repo}/issues/{number}")

    def repository(self, owner, repo):
        return self.request("GET", f"/repos/{owner}/{repo}")

    def tree(self, owner, repo, branch):
        ref = self.request("GET", f"/repos/{owner}/{repo}/git/ref/heads/{branch}")
        sha = ref["object"]["sha"]
        commit = self.request("GET", f"/repos/{owner}/{repo}/git/commits/{sha}")
        return self.request("GET", f"/repos/{owner}/{repo}/git/trees/{commit['tree']['sha']}", params={"recursive": 1})

    def file(self, owner, repo, path, ref):
        return self.request("GET", f"/repos/{owner}/{repo}/contents/{path}", params={"ref": ref})

    def create_pull_request(self, owner, repo, title, body, head, base):
        return self.request("POST", f"/repos/{owner}/{repo}/pulls",
                            json={"title": title, "body": body, "head": head, "base": base, "draft": True})
