
import sys
from pathlib import Path
from dotenv import load_dotenv

# Make the project root importable when running this from tests/
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from providers.gemini import GeminiProvider
from models import ReviewComment


class Color:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    GREEN = "\033[32m"
    RED = "\033[31m"
    YELLOW = "\033[33m"
    CYAN = "\033[36m"


FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"


def run_fixture(provider: GeminiProvider, path: Path) -> list[ReviewComment]:
    diff = path.read_text(encoding="utf-8")
    return provider.review_diff(diff)


def main():
    load_dotenv()
    provider = GeminiProvider()
    
    fixtures = sorted(FIXTURES_DIR.glob("*.diff"))
    if not fixtures:
        print(f"{Color.RED}No fixtures found in {FIXTURES_DIR}{Color.RESET}")
        sys.exit(1)
    
    print(f"{Color.BOLD}Running {len(fixtures)} fixtures{Color.RESET}\n")
    
    for fixture in fixtures:
        print(f"{Color.CYAN}─── {fixture.name} ───{Color.RESET}")
        try:
            comments = run_fixture(provider, fixture)
        except Exception as e:
            print(f"  {Color.RED}ERROR:{Color.RESET} {e}\n")
            continue
        
        if not comments:
            print(f"  {Color.DIM}(no comments){Color.RESET}\n")
            continue
        
        for c in comments:
            print(f"  [{c.severity.value:8}] {c.category.value:14} L{c.line}: {c.comment[:120]}")
        print()


if __name__ == "__main__":
    main()