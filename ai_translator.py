"""
ai_translator.py
------------------
Defines the AITranslator class - sends technical/clinical drug text to
Google's Gemini API and gets back a plain-language rewrite.

Uses Gemini's REST API directly via the `requests` library (matching the
tech stack listed in the assignment), rather than installing Google's
separate SDK - keeps the dependency list simple.

You need a Gemini API key for this class to work. Get one free at
https://aistudio.google.com -> "Get API key". Store it as an environment
variable called GEMINI_API_KEY rather than typing it directly into this
file, so it never accidentally gets pushed to GitHub.
"""

import os
import requests

GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"


class AITranslator:
    """Handles rewriting technical medical text into plain language using Gemini."""

    def __init__(self, api_key: str = None):
        """
        api_key can be passed in directly, but by default this looks for
        an environment variable called GEMINI_API_KEY. Using an environment
        variable means the key lives on your computer, not inside this
        file - so it's never at risk of being committed to GitHub by accident.
        """
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")

    def translate(self, technical_text: str) -> str:
        """
        Send technical_text to Gemini and return a plain-language rewrite.
        If the API key is missing, or the request fails for any reason,
        this returns the ORIGINAL text with a note attached, rather than
        crashing the whole program - a failed AI rewrite shouldn't stop
        the user from at least seeing the raw information.
        """
        if not self.api_key:
            return f"[AI translation unavailable - no API key set] {technical_text}"

        if not technical_text or technical_text.strip() == "":
            return "Not specified."

        prompt = (
            "Rewrite the following medical text in simple, everyday language "
            "that a patient with no medical background could easily understand. "
            "Keep it to 1-2 short sentences.\n\n"
            f"Text: {technical_text}"
        )

        request_body = {
            "contents": [
                {"parts": [{"text": prompt}]}
            ]
        }

        try:
            response = requests.post(
                GEMINI_URL,
                headers={"x-goog-api-key": self.api_key},
                json=request_body,
                timeout=15
            )
            response.raise_for_status()
        except requests.exceptions.RequestException as error:
            return f"[AI translation failed: {error}] Original: {technical_text}"

        try:
            data = response.json()
            plain_text = data["candidates"][0]["content"]["parts"][0]["text"]
            return plain_text.strip()
        except (KeyError, IndexError):
            # The response came back successfully, but not in the shape
            # we expected - happens occasionally with any external API.
            return f"[Unexpected AI response format] Original: {technical_text}"
