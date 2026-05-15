"""GitHub API client. Fetches PR diffs and metadata."""

import os
from dataclasses import dataclass
import requests


GITHUB_API_BASE = "https://api.github.com"


@dataclass
class PRMetadata:
    """Information needed to fetch the source code of a PR."""
    head_repo_clone_url: str  # e.g. "https://github.com/user/repo.git"
    head_branch: str           # e.g. "feature-branch"
    head_sha: str              # commit SHA at the tip of head_branch
    base_repo_full_name: str   # "owner/repo" of the target repo


class GitHubClient:
    """Minimal GitHub API client for PR review workflows."""

    def __init__(self):
        token = os.environ.get("GITHUB_TOKEN")
        if not token:
            raise RuntimeError(
                "GITHUB_TOKEN not found. Add it to .env in the project root."
            )
        
        self.token = token
        self.json_headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        self.diff_headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github.v3.diff",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    def fetch_pr_diff(self, owner: str, repo: str, pr_number: int) -> str:
        """Fetch the unified diff for a pull request."""
        url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/pulls/{pr_number}"
        response = requests.get(url, headers=self.diff_headers, timeout=30)
        self._check_response(response, owner, repo, pr_number)
        return response.text

    def fetch_pr_metadata(self, owner: str, repo: str, pr_number: int) -> PRMetadata:
        """Fetch the metadata needed to clone the PR's branch."""
        url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/pulls/{pr_number}"
        response = requests.get(url, headers=self.json_headers, timeout=30)
        self._check_response(response, owner, repo, pr_number)
        
        data = response.json()
        return PRMetadata(
            head_repo_clone_url=data["head"]["repo"]["clone_url"],
            head_branch=data["head"]["ref"],
            head_sha=data["head"]["sha"],
            base_repo_full_name=data["base"]["repo"]["full_name"],
        )

    @staticmethod
    def _check_response(response, owner: str, repo: str, pr_number: int) -> None:
        if response.status_code == 404:
            raise RuntimeError(
                f"PR not found: {owner}/{repo}#{pr_number}. "
                "Check the owner, repo name, and PR number."
            )
        if response.status_code == 403:
            raise RuntimeError(
                "GitHub returned 403. Likely rate limit or insufficient token scope."
            )
        if response.status_code != 200:
            raise RuntimeError(
                f"GitHub API error {response.status_code}: {response.text[:200]}"
            )