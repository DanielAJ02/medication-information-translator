import os
from google import genai


class AITranslator:
    """Handles rewriting technical medical text into plain language using Gemini."""

    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")

        if self.api_key:
            self.client = genai.Client(api_key=self.api_key)
        else:
            self.client = None

    def translate(self, technical_text: str) -> str:
        """Send technical medical text to Gemini for simplification."""

        if not technical_text or technical_text.strip() == "":
            return "Not specified."

        if not self.client:
            return (
                "[AI translation unavailable - no API key set] "
                f"{technical_text}"
            )

        prompt = (
            "Rewrite the following medical text in simple, everyday language "
            "that a patient with no medical background could easily understand. "
            "Keep it to 1-2 short sentences. "
            "Do not change the medical meaning and do not add information.\n\n"
            f"Text: {technical_text}"
        )

        try:
            response = self.client.models.generate_content(
                model="gemini-3.6-flash",
                contents=prompt,
            )

            if response.text:
                return response.text.strip()

            return (
                "[Empty AI response] "
                f"Original: {technical_text}"
            )

        except Exception as error:
            return (
                f"[AI translation failed: {error}] "
                f"Original: {technical_text}"
            )