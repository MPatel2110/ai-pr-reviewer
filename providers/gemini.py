import os
from google import genai
from .base import LLMProvider


class GeminiProvider(LLMProvider):
    """LLM provider backed by Google's Gemini API."""

    def __init__(self, model: str = "gemini-2.5-flash"):
        """
        Initialize the Gemini client.
        
        Args:
            model: Gemini model identifier. Default is gemini-2.5-flash —
                   fast, cheap, and on the free tier. Upgrade to gemini-2.5-pro
                   for harder reasoning later if needed.
        """
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError(
                "GEMINI_API_KEY not found. Make sure .env exists in the "
                "project root and load_dotenv() ran before this."
            )
        
        self.client = genai.Client(api_key=api_key)
        self.model = model

    def review_diff(self, diff: str) -> str:
        """Send the diff to Gemini and return the raw text response."""
        prompt = (
            "You are a senior code reviewer. Review the following code diff "
            "and identify bugs, security issues, or quality problems. Be "
            "specific and reference line content where relevant.\n\n"
            f"Diff:\n```\n{diff}\n```"
        )
        
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
        )
        return response.text