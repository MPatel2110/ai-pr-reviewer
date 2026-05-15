"""Abstract base class defining the contract for all LLM providers."""

from abc import ABC, abstractmethod
from pathlib import Path

from models import ReviewComment


class LLMProvider(ABC):
    """
    Contract that every LLM provider must fulfill.
    """

    @abstractmethod
    def review_diff(
        self,
        diff: str,
        context_files: list[tuple[Path, str]] | None = None,
    ) -> list[ReviewComment]:
        """
        Send a code diff to the LLM and return structured review comments.
        
        Args:
            diff: A unified-diff-format string representing code changes.
            context_files: Optional list of (path, content) for related files
                that may help the model reason about the diff. Pass None or []
                to disable context-aware review.
        
        Returns:
            A list of ReviewComment objects. Empty list means no issues found.
        """
        pass