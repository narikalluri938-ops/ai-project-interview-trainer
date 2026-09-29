import logging
from pathlib import Path
from typing import List, Dict, Any
from app.models import db, Project, Question
from .ai_providers import get_ai_provider

logger = logging.getLogger(__name__)

PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"

def load_prompt_template(filename: str) -> str:
    path = PROMPTS_DIR / filename
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def generate_questions_for_project(project: Project, force_regenerate: bool = False) -> List[Question]:
    """
    Generates realistic, technology-specific questions across:
    - Basic
    - Technical
    - Why / Trade-offs
    - Scenario & Troubleshooting
    - Follow-up
    """
    if not force_regenerate and project.questions.count() > 0:
        return project.questions.all()

    template = load_prompt_template("question_generation.txt")
    
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
        "{{ individual_contribution }}": project.individual_contribution or project.role or ""
    }
    
    for k, v in replacements.items():
        prompt = prompt.replace(k, str(v))

    provider = get_ai_provider()
    try:
        data = provider.generate_json(prompt=prompt)
    except Exception as e:
        logger.error(f"Error calling AI provider for question generation: {e}. Falling back to MockProvider.")
        from .ai_providers.mock_provider import MockProvider
        data = MockProvider().generate_json(prompt=prompt)

    raw_questions = data.get("questions", []) if isinstance(data, dict) else []
    if not raw_questions:
        from .ai_providers.mock_provider import MockProvider
        data = MockProvider().generate_json(prompt=prompt)
        raw_questions = data.get("questions", [])

    # If force regenerating, delete existing questions that are not tied to answers
    if force_regenerate:
        # Delete questions that have no answers, or clear all
        for q in project.questions.all():
            db.session.delete(q)
        db.session.commit()

    created_questions = []
    valid_categories = {"basic", "technical", "why", "scenario", "follow_up"}
    valid_difficulties = {"beginner", "intermediate", "advanced", "expert"}

    for item in raw_questions:
        if not isinstance(item, dict) or not item.get("question"):
            continue
        
        category = item.get("category", "technical").lower()
        if category not in valid_categories:
            category = "technical"
            
        difficulty = item.get("difficulty", "intermediate").lower()
        if difficulty not in valid_difficulties:
            difficulty = "intermediate"

        q = Question(
            project_id=project.id,
            category=category,
            question=item.get("question", "").strip(),
            difficulty=difficulty,
            expected_concepts=item.get("expected_concepts", ""),
            interview_tips=item.get("interview_tips", ""),
            tradeoffs=item.get("tradeoffs", "")
        )
        db.session.add(q)
        created_questions.append(q)

    db.session.commit()
    return created_questions
