import json
import logging
import requests
from typing import Optional
from .base import AIProvider

logger = logging.getLogger(__name__)

class OpenAIProvider(AIProvider):
    """OpenAI API provider using REST endpoint."""

    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        self.api_key = api_key
        self.model = model or "gpt-4o-mini"
        self.url = "https://api.openai.com/v1/chat/completions"

    def generate_completion(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        json_mode: bool = True,
        max_tokens: int = 2500,
        temperature: float = 0.7
    ) -> str:
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY is not configured.")

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        if json_mode:
            payload["response_format"] = {"type": "json_object"}

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(self.url, headers=headers, json=payload, timeout=45)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except requests.exceptions.RequestException as e:
            status_code = getattr(getattr(e, "response", None), "status_code", "Unknown")
            logger.error(f"OpenAI API request failed with status {status_code}")
            raise RuntimeError(f"OpenAI API request failed (HTTP {status_code})")
