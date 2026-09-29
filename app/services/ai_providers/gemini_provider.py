import json
import logging
import requests
from typing import Optional
from .base import AIProvider

logger = logging.getLogger(__name__)

class GeminiProvider(AIProvider):
    """Google Gemini API provider using official REST endpoint."""

    def __init__(self, api_key: str, model: str = "gemini-2.5-flash"):
        self.api_key = api_key
        self.model = model or "gemini-2.5-flash"
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"

    def generate_completion(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        json_mode: bool = True,
        max_tokens: int = 2500,
        temperature: float = 0.7
    ) -> str:
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is not configured.")

        url = f"{self.base_url}/{self.model}:generateContent"

        contents = []
        if system_prompt:
            contents.append({"role": "user", "parts": [{"text": f"System Instructions: {system_prompt}"}]})
            contents.append({"role": "model", "parts": [{"text": "Understood. I will strictly follow these instructions."}]})

        contents.append({"role": "user", "parts": [{"text": prompt}]})

        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
            }
        }

        if json_mode:
            payload["generationConfig"]["responseMimeType"] = "application/json"

        # Pass key via header for security, avoiding exposure in URL query strings or network logs
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": self.api_key
        }

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=45)
            response.raise_for_status()
            data = response.json()
            
            candidates = data.get("candidates", [])
            if candidates and "content" in candidates[0]:
                parts = candidates[0]["content"].get("parts", [])
                if parts:
                    return parts[0].get("text", "")
            return ""
        except requests.exceptions.RequestException as e:
            status_code = getattr(getattr(e, "response", None), "status_code", "Unknown")
            logger.error(f"Gemini API request failed with status {status_code}")
            raise RuntimeError(f"Gemini API request failed (HTTP {status_code})")
