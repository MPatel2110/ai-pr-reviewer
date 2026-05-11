import os
import requests


GITHUB_API_BASE = "https://api.github.com"


class GitHubClient:
    """Minimal GitHub API client for fetching PR diffs."""

    def __init__(self):
        token = os.environ.get("GITHUB_TOKEN")
        if not token:
            raise RuntimeError(
                "GITHUB_TOKEN not found. Add it to .env in the project root."
            )
        
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github.v3.diff",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    def fetch_pr_diff(self, owner: str, repo: str, pr_number: int) -> str:
        """
        Fetch the unified diff for a pull request.
        
        Args:
            owner: GitHub username or org (e.g. "MPatel2110")
            repo: Repository name (e.g. "marvel-rivals-tracker")
            pr_number: Pull request number
        
        Returns:
            The PR's diff as a unified-diff-format string.
        
        Raises:
            RuntimeError: If the PR cannot be fetched (404, 403, network error, etc.)
        """
        url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/pulls/{pr_number}"
        
        response = requests.get(url, headers=self.headers, timeout=30)
        
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
        
        return response.text