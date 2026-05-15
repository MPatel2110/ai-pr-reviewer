"""Clone a PR's source branch to a temporary directory."""

import os
import shutil
import subprocess
import tempfile
from contextlib import contextmanager
from pathlib import Path

from github_client import PRMetadata


@contextmanager
def fetch_pr_repo(metadata: PRMetadata):
    """
    Context manager that clones the PR's branch into a temp dir and cleans up after.
    
    Usage:
        with fetch_pr_repo(metadata) as repo_path:
            # repo_path is a Path to the cloned repo root
            ...
        # Temp dir is automatically deleted on exit
    
    Args:
        metadata: PR metadata from GitHubClient.fetch_pr_metadata()
    
    Yields:
        pathlib.Path pointing to the cloned repo root.
    
    Raises:
        RuntimeError: If git is not installed or the clone fails.
    """
    temp_dir = Path(tempfile.mkdtemp(prefix="ai-pr-reviewer-"))
    
    try:
        # Inject the auth token into the clone URL for private repos.
        # For public repos this is unnecessary but harmless.
        token = os.environ.get("GITHUB_TOKEN", "")
        auth_url = metadata.head_repo_clone_url.replace(
            "https://", f"https://x-access-token:{token}@", 1
        )
        
        # Shallow clone (depth=1) at the specific branch. Fast and small.
        result = subprocess.run(
            [
                "git", "clone",
                "--depth", "1",
                "--branch", metadata.head_branch,
                "--quiet",
                auth_url,
                str(temp_dir),
            ],
            capture_output=True,
            text=True,
            timeout=120,
        )
        
        if result.returncode != 0:
            # Strip the token out of error messages so it never gets logged
            error = result.stderr.replace(token, "***") if token else result.stderr
            raise RuntimeError(f"git clone failed: {error}")
        
        yield temp_dir
    
    finally:
        # Always clean up, even if the body raised.
        # ignore_errors=True because Windows occasionally locks files in .git/
        shutil.rmtree(temp_dir, ignore_errors=True)