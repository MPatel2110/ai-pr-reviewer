"""AI PR Reviewer CLI. Fetches a GitHub PR, reviews each file, prints structured comments."""

import argparse
import sys
from pathlib import Path

from dotenv import load_dotenv

from github_client import GitHubClient
from diff_filter import parse_and_filter_diff
from import_resolver import find_local_imports, select_context_files
from models import ReviewComment, Severity
from providers.gemini import GeminiProvider
from repo_fetcher import fetch_pr_repo


class Color:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RED = "\033[31m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"


SEVERITY_COLOR = {
    Severity.INFO: Color.BLUE,
    Severity.WARNING: Color.YELLOW,
    Severity.ERROR: Color.RED,
    Severity.CRITICAL: Color.MAGENTA,
}


def parse_pr_argument(pr_arg: str) -> tuple[str, str]:
    if pr_arg.count("/") != 1:
        raise ValueError(
            f"Invalid --pr format: '{pr_arg}'. Expected 'owner/repo' "
            "(e.g. 'MPatel2110/ai-pr-reviewer')."
        )
    owner, repo = pr_arg.split("/")
    if not owner or not repo:
        raise ValueError(f"Invalid --pr format: '{pr_arg}'.")
    return owner, repo


def print_comments(file_path: str, comments: list[ReviewComment]) -> None:
    if not comments:
        return
    print(f"\n{Color.BOLD}{Color.CYAN}{file_path}{Color.RESET}  "
          f"{Color.DIM}({len(comments)} comment(s)){Color.RESET}")
    print(Color.DIM + "─" * 60 + Color.RESET)
    for c in sorted(comments, key=lambda x: x.line):
        color = SEVERITY_COLOR[c.severity]
        severity_label = f"{color}{c.severity.value.upper():8}{Color.RESET}"
        print(f"  {severity_label} L{c.line:<4}  {Color.DIM}{c.category.value}{Color.RESET}")
        print(f"           {c.comment}")


def main():
    parser = argparse.ArgumentParser(
        description="AI-powered code review for GitHub pull requests."
    )
    parser.add_argument("--pr", required=True, metavar="OWNER/REPO",
                        help="Repository in 'owner/repo' format")
    parser.add_argument("pr_number", type=int, help="Pull request number")
    parser.add_argument("--no-context", action="store_true",
                        help="Disable context-aware review (faster, less accurate)")
    args = parser.parse_args()
    
    load_dotenv()
    
    try:
        owner, repo = parse_pr_argument(args.pr)
    except ValueError as e:
        print(f"{Color.RED}Error:{Color.RESET} {e}", file=sys.stderr)
        sys.exit(1)
    
    print(f"{Color.DIM}Fetching PR {owner}/{repo}#{args.pr_number}...{Color.RESET}")
    github = GitHubClient()
    
    try:
        raw_diff = github.fetch_pr_diff(owner, repo, args.pr_number)
        metadata = github.fetch_pr_metadata(owner, repo, args.pr_number)
    except RuntimeError as e:
        print(f"{Color.RED}Error:{Color.RESET} {e}", file=sys.stderr)
        sys.exit(1)
    
    reviewable_files = parse_and_filter_diff(raw_diff)
    if not reviewable_files:
        print(f"{Color.YELLOW}No reviewable files in this PR.{Color.RESET}")
        return
    
    print(f"{Color.DIM}Reviewing {len(reviewable_files)} file(s)...{Color.RESET}")
    provider = GeminiProvider()
    
    if args.no_context:
        # Fast path: review each file's diff with no repo context.
        _review_without_context(provider, reviewable_files)
        return
    
    # Context-aware path: clone the PR branch and resolve imports per file.
    print(f"{Color.DIM}Cloning repo for context...{Color.RESET}")
    try:
        with fetch_pr_repo(metadata) as repo_path:
            _review_with_context(provider, reviewable_files, repo_path)
    except RuntimeError as e:
        print(f"{Color.YELLOW}Warning:{Color.RESET} clone failed ({e}); "
              "falling back to no-context review.", file=sys.stderr)
        _review_without_context(provider, reviewable_files)


def _review_without_context(
    provider: GeminiProvider,
    reviewable_files: list[tuple[str, str]],
) -> None:
    total = 0
    for file_path, file_diff in reviewable_files:
        comments = provider.review_diff(file_diff)
        print_comments(file_path, comments)
        total += len(comments)
    _print_summary(total, len(reviewable_files))


def _review_with_context(
    provider: GeminiProvider,
    reviewable_files: list[tuple[str, str]],
    repo_path: Path,
) -> None:
    total = 0
    for file_path, file_diff in reviewable_files:
        context = _build_context_for(file_path, repo_path)
        if context:
            ctx_names = ", ".join(p.name for p, _ in context)
            print(f"  {Color.DIM}context for {file_path}: {ctx_names}{Color.RESET}")
        
        comments = provider.review_diff(file_diff, context_files=context)
        print_comments(file_path, comments)
        total += len(comments)
    _print_summary(total, len(reviewable_files))
    

def _build_context_for(file_path: str, repo_path: Path) -> list[tuple[Path, str]]:
    """Resolve imports of file_path and return selected context files."""
    full_path = repo_path / file_path
    if not full_path.is_file():
        return []
    
    try:
        content = full_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return []
    
    candidates = find_local_imports(content, repo_path, full_path)
    return select_context_files(candidates)


def _print_summary(total_comments: int, file_count: int) -> None:
    print()
    print(Color.DIM + "═" * 60 + Color.RESET)
    if total_comments == 0:
        print(f"{Color.BOLD}✓ No issues found across {file_count} file(s).{Color.RESET}")
    else:
        print(f"{Color.BOLD}{total_comments} comment(s) across {file_count} file(s).{Color.RESET}")


if __name__ == "__main__":
    main()