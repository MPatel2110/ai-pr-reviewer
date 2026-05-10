"""Gemini implementation of the LLMProvider contract."""

import os
from google import genai
from google.genai import types
from .base import LLMProvider
from models import ReviewComment


SYSTEM_PROMPT = """You are a senior code reviewer. Analyze the provided code diff and identify issues.

For each issue you find, produce a structured comment specifying:
- The file path (from the diff header)
- The line number in the new version of the file
- The severity (info, warning, error, or critical)
- The category (bug, security, performance, style, or documentation)
- A specific, actionable comment explaining the issue

Only flag real issues. Do not invent problems. If the diff has no issues, return an empty list.
Do not include positive feedback or general commentary — only actionable comments tied to specific lines."""


class GeminiProvider(LLMProvider):
    """LLM provider backed by Google's Gemini API."""

    def __init__(self, model: str = "gemini-2.5-flash"):
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError(
                "GEMINI_API_KEY not found. Make sure .env exists in the "
                "project root and load_dotenv() ran before this."
            )
        
        self.client = genai.Client(api_key=api_key)
        self.model = model

    def review_diff(self, diff: str) -> list[ReviewComment]:
        """Send the diff to Gemini and return validated review comments."""
        prompt = f"{SYSTEM_PROMPT}\n\nDiff:\n```\n{diff}\n```"
        
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=list[ReviewComment],
            ),
        )
        
        # Gemini's SDK auto-parses the response into our Pydantic models
        return response.parsed or []