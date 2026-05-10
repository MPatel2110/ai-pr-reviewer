from abc import ABC, abstractmethod
from models import ReviewComment


class LLMProvider(ABC):
    """
    Contract that every LLM provider must fulfill.
    
    Any new provider (Claude, GPT, Llama, etc.) subclasses this and
    implements review_diff(). The rest of the app talks to providers
    only through this interface, so swapping providers requires no
    changes to calling code.
    """

    @abstractmethod
    def review_diff(self, diff: str) -> list[ReviewComment]:
        """
        Send a code diff to the LLM and return structured review comments.
        
        Args:
            diff: A unified-diff-format string representing code changes.
        
        Returns:
            A list of ReviewComment objects. Empty list means no issues found.
            The list is never None — providers must return [] for clean diffs.
        """
        pass