import re
import json
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class AIProvider(ABC):
    """Abstract base class for all AI providers."""

    @abstractmethod
    def generate_completion(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        json_mode: bool = True,
        max_tokens: int = 2500,
        temperature: float = 0.7
    ) -> str:
        """Generate text completion from provider."""
        pass

    def generate_json(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 2500,
        temperature: float = 0.5
    ) -> Dict[str, Any]:
        """Generate structured JSON and safely parse it."""
        raw_response = self.generate_completion(
            prompt=prompt,
            system_prompt=system_prompt,
            json_mode=True,
            max_tokens=max_tokens,
            temperature=temperature
        )
        return self.extract_json(raw_response)

    @staticmethod
    def extract_json(text: str) -> Dict[str, Any]:
        """Robustly extracts JSON from an LLM response even if surrounded by markdown code fences."""
        if not text:
            return {}
        
        # 1. Try direct parsing
        text = text.strip()
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # 2. Extract from markdown code fence ```json ... ``` or ``` ... ```
        pattern = r"```(?:json)?\s*([\s\S]*?)\s*```"
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            clean_str = match.group(1).strip()
            try:
                return json.loads(clean_str)
            except json.JSONDecodeError:
                pass

        # 3. Look for the first '{' and last '}'
        start_idx = text.find("{")
        end_idx = text.rfind("}")
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            substring = text[start_idx : end_idx + 1]
            try:
                return json.loads(substring)
            except json.JSONDecodeError:
                pass

        # 4. Look for an array '[' and ']'
        arr_start = text.find("[")
        arr_end = text.rfind("]")
        if arr_start != -1 and arr_end != -1 and arr_end > arr_start:
            substring = text[arr_start : arr_end + 1]
            try:
                return {"items": json.loads(substring)}
            except json.JSONDecodeError:
                pass

        logger.error(f"Failed to parse JSON from AI response: {text[:200]}...")
        return {}
