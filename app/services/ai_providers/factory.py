import os
import logging
from flask import current_app
from .base import AIProvider
from .mock_provider import MockProvider
from .gemini_provider import GeminiProvider
from .openai_provider import OpenAIProvider

logger = logging.getLogger(__name__)

def get_ai_provider() -> AIProvider:
    """
    Factory function returning the configured AIProvider instance.
    Gracefully falls back to MockProvider if credentials are missing or errors occur.
    """
    try:
        provider_name = current_app.config.get("AI_PROVIDER", "mock").lower()
        api_key = current_app.config.get("AI_API_KEY", "")
        model = current_app.config.get("AI_MODEL", "")
    except RuntimeError:
        # Outside Flask application context (e.g. standalone test/script)
        provider_name = os.getenv("AI_PROVIDER", "mock").lower()
        api_key = os.getenv("AI_API_KEY", "")
        model = os.getenv("AI_MODEL", "")

    if provider_name == "gemini":
        if api_key:
            return GeminiProvider(api_key=api_key, model=model or "gemini-2.5-flash")
        logger.warning("AI_PROVIDER is 'gemini' but no AI_API_KEY provided. Falling back to MockProvider.")
        return MockProvider()

    elif provider_name in ["openai", "chatgpt"]:
        if api_key:
            return OpenAIProvider(api_key=api_key, model=model or "gpt-4o-mini")
        logger.warning("AI_PROVIDER is 'openai' but no AI_API_KEY provided. Falling back to MockProvider.")
        return MockProvider()

    # Default to high-quality MockProvider
    return MockProvider()
