import argparse
import sys
from dotenv import load_dotenv

from github_client import GitHubClient
from diff_filter import parse_and_filter_diff
from providers.gemini import GeminiProvider
from models import ReviewComment, Severity


# ANSI color codes for terminal output. No external dependency for this much color.
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
    """Parse 'owner/repo' into (owner, repo). Raises if malformed."""
    if pr_arg.count("/") != 1:
        raise ValueError(
            f"Invalid --pr format: '{pr_arg}'. Expected 'owner/repo' (e.g. 'MPatel2110/ai-pr-reviewer')."
        )
    owner, repo = pr_arg.split("/")
    if not owner or not repo:
        raise ValueError(f"Invalid --pr format: '{pr_arg}'. Owner and repo must both be non-empty.")
    return owner, repo


def print_comments(file_path: str, comments: list[ReviewComment]) -> None:
    """Print review comments for a single file, grouped under the file path."""
    if not comments:
        return
    
    print(f"\n{Color.BOLD}{Color.CYAN}{file_path}{Color.RESET}  {Color.DIM}({len(comments)} comment(s)){Color.RESET}")
    print(Color.DIM + "─" * 60 + Color.RESET)
    
    # Sort by line number for readability
    for c in sorted(comments, key=lambda x: x.line):
        color = SEVERITY_COLOR[c.severity]
        severity_label = f"{color}{c.severity.value.upper():8}{Color.RESET}"
        print(f"  {severity_label} L{c.line:<4}  {Color.DIM}{c.category.value}{Color.RESET}")
        print(f"           {c.comment}")


def main():
    parser = argparse.ArgumentParser(
        description="AI-powered code review for GitHub pull requests."
    )
    parser.add_argument(
        "--pr",
        required=True,
        metavar="OWNER/REPO",
        help="Repository in 'owner/repo' format (e.g. 'MPatel2110/ai-pr-reviewer')",
    )
    parser.add_argument(
        "pr_number",
        type=int,
        help="Pull request number to review",
    )
    args = parser.parse_args()
    
    load_dotenv()
    
    # Parse the --pr argument
    try:
        owner, repo = parse_pr_argument(args.pr)
    except ValueError as e:
        print(f"{Color.RED}Error:{Color.RESET} {e}", file=sys.stderr)
        sys.exit(1)
    
    # Fetch the diff
    print(f"{Color.DIM}Fetching PR {owner}/{repo}#{args.pr_number}...{Color.RESET}")
    try:
        github = GitHubClient()
        raw_diff = github.fetch_pr_diff(owner, repo, args.pr_number)
    except RuntimeError as e:
        print(f"{Color.RED}Error:{Color.RESET} {e}", file=sys.stderr)
        sys.exit(1)
    
    # Parse and filter
    reviewable_files = parse_and_filter_diff(raw_diff)
    if not reviewable_files:
        print(f"{Color.YELLOW}No reviewable files in this PR.{Color.RESET}")
        print(f"{Color.DIM}(Only Python files are reviewed in Day 3 scope.){Color.RESET}")
        return
    
    print(f"{Color.DIM}Reviewing {len(reviewable_files)} file(s)...{Color.RESET}")
    
    # Review each file
    provider = GeminiProvider()
    total_comments = 0
    
    for file_path, file_diff in reviewable_files:
        comments = provider.review_diff(file_diff)
        print_comments(file_path, comments)
        total_comments += len(comments)
    
    # Summary
    print()
    print(Color.DIM + "═" * 60 + Color.RESET)
    if total_comments == 0:
        print(f"{Color.BOLD}✓ No issues found across {len(reviewable_files)} file(s).{Color.RESET}")
    else:
        print(f"{Color.BOLD}{total_comments} comment(s) across {len(reviewable_files)} file(s).{Color.RESET}")


if __name__ == "__main__":
    main()