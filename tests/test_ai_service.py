import json
import pytest
from app.services.ai_providers.base import AIProvider
from app.services.ai_providers.mock_provider import MockProvider
from app.services.ai_providers.factory import get_ai_provider

def test_extract_json_direct():
    data = {"key": "value", "list": [1, 2, 3]}
    raw = json.dumps(data)
    parsed = AIProvider.extract_json(raw)
    assert parsed == data

def test_extract_json_with_code_fences():
    raw = "```json\n{\n  \"score\": 95,\n  \"status\": \"passed\"\n}\n```"
    parsed = AIProvider.extract_json(raw)
    assert parsed.get("score") == 95
    assert parsed.get("status") == "passed"

def test_extract_json_with_surrounding_conversational_text():
    raw = "Sure! Here is the output you requested:\n\n{\"answer\": \"correct\", \"points\": 10}\n\nHope this helps!"
    parsed = AIProvider.extract_json(raw)
    assert parsed.get("answer") == "correct"
    assert parsed.get("points") == 10

def test_extract_json_invalid():
    raw = "This contains no valid json at all."
    parsed = AIProvider.extract_json(raw)
    assert parsed == {}

def test_mock_provider_generation():
    provider = MockProvider()
    response = provider.generate_completion("Analyze the following student project:\nProject Name: Test Project\nTechnologies: Python, Flask")
    parsed = json.loads(response)
    assert "explanations" in parsed
    assert "thirty_second" in parsed["explanations"]
    assert "risk_areas" in parsed

def test_factory_fallback():
    provider = get_ai_provider()
    assert isinstance(provider, MockProvider)

def test_gemini_provider_missing_key():
    from app.services.ai_providers.gemini_provider import GeminiProvider
    provider = GeminiProvider(api_key="")
    with pytest.raises(ValueError) as exc:
        provider.generate_completion("Test prompt")
    assert "GEMINI_API_KEY is not configured" in str(exc.value)

def test_openai_provider_missing_key():
    from app.services.ai_providers.openai_provider import OpenAIProvider
    provider = OpenAIProvider(api_key="")
    with pytest.raises(ValueError) as exc:
        provider.generate_completion("Test prompt")
    assert "OPENAI_API_KEY is not configured" in str(exc.value)

def test_sanitized_gemini_error_on_network_failure(monkeypatch):
    import requests
    from app.services.ai_providers.gemini_provider import GeminiProvider

    def mock_post(*args, **kwargs):
        err = requests.exceptions.RequestException("Network connection reset")
        raise err

    monkeypatch.setattr(requests, "post", mock_post)
    provider = GeminiProvider(api_key="super_secret_test_key_12345")
    with pytest.raises(RuntimeError) as exc:
        provider.generate_completion("Test prompt")
    # Verify the secret key is NOT in the error message
    assert "super_secret_test_key_12345" not in str(exc.value)
    assert "Gemini API request failed" in str(exc.value)

def test_sanitized_openai_error_on_network_failure(monkeypatch):
    import requests
    from app.services.ai_providers.openai_provider import OpenAIProvider

    def mock_post(*args, **kwargs):
        err = requests.exceptions.RequestException("Network connection reset")
        raise err

    monkeypatch.setattr(requests, "post", mock_post)
    provider = OpenAIProvider(api_key="super_secret_openai_key_99999")
    with pytest.raises(RuntimeError) as exc:
        provider.generate_completion("Test prompt")
    # Verify the secret key is NOT in the error message
    assert "super_secret_openai_key_99999" not in str(exc.value)
    assert "OpenAI API request failed" in str(exc.value)

