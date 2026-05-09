from abc import ABC, abstractmethod


class LLMProvider(ABC):
    """
    Contract that every LLM provider must fulfill.
    
    Any new provider (Claude, GPT, Llama, etc.) subclasses this and
    implements review_diff(). The rest of the app talks to providers
    only through this interface, so swapping providers requires no
    changes to calling code.
    """

    @abstractmethod
    def review_diff(self, diff: str) -> str:
        """
        Send a code diff to the LLM and return its review as plain text.
        
        Args:
            diff: A unified-diff-format string representing code changes.
        
        Returns:
            The LLM's review response as a string. Format is unstructured
            for now; Day 2 introduces structured JSON output.
        """
        pass