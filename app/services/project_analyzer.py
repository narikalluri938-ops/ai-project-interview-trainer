import os
import logging
from pathlib import Path
from typing import Dict, Any
from app.models import db, Project
from .ai_providers import get_ai_provider

logger = logging.getLogger(__name__)

PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"

def load_prompt_template(filename: str) -> str:
    path = PROMPTS_DIR / filename
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def analyze_project(project: Project) -> Dict[str, Any]:
    """
    Performs deep architectural and risk analysis on a student's project.
    Strictly follows anti-hallucination rules and generates 5 explanation tiers,
    detected risks, and core learning topics.
    """
    template = load_prompt_template("project_analysis.txt")
    
    # Fill placeholders
    prompt = template
    replacements = {
        "{{ name }}": project.name or "",
        "{{ role }}": project.role or "",
        "{{ technologies }}": project.technologies or "",
        "{{ description }}": project.description or "",
        "{{ features }}": project.features or "Not specified",
        "{{ algorithms }}": project.algorithms or "Not specified",
        "{{ database }}": project.database or "Not specified",
        "{{ apis }}": project.apis or "Not specified",
        "{{ challenges }}": project.challenges or "Not specified",
        "{{ deployment }}": project.deployment or "Not specified",
        "{{ team_size }}": project.team_size or "Individual",
        "{{ individual_contribution }}": project.individual_contribution or project.role or "",
        "{{ additional_notes }}": project.additional_notes or "None"
    }
    
    for k, v in replacements.items():
        prompt = prompt.replace(k, str(v))

    provider = get_ai_provider()
    try:
        data = provider.generate_json(prompt=prompt)
    except Exception as e:
        logger.error(f"Error calling AI provider for project analysis: {e}. Falling back to MockProvider.")
        from .ai_providers.mock_provider import MockProvider
        data = MockProvider().generate_json(prompt=prompt)

    # Ensure required top-level keys exist
    if not isinstance(data, dict) or "explanations" not in data:
        from .ai_providers.mock_provider import MockProvider
        data = MockProvider().generate_json(prompt=prompt)

    # Save to project
    project.analysis = data
    db.session.commit()
    return data
