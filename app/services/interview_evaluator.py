import logging
from pathlib import Path
from typing import Dict, Any
from app.models import db, Interview, Question, Answer
from .ai_providers import get_ai_provider

logger = logging.getLogger(__name__)

PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"

def load_prompt_template(filename: str) -> str:
    path = PROMPTS_DIR / filename
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def evaluate_student_answer(interview: Interview, question: Question, student_answer: str) -> Answer:
    """
    Evaluates candidate's answer against project context, computes multi-dimensional
    scores, extracts strengths, gaps, corrections, and generates a dynamic follow-up.
    """
    project = interview.project
    template = load_prompt_template("interview_evaluation.txt")
    
    prompt = template
    replacements = {
        "{{ project_name }}": project.name or "",
        "{{ technologies }}": project.technologies or "",
        "{{ role }}": project.role or "",
        "{{ question }}": question.question or "",
        "{{ category }}": question.category or "",
        "{{ expected_concepts }}": question.expected_concepts or "Core principles and implementation details",
        "{{ current_difficulty }}": question.difficulty or "intermediate",
        "{{ student_answer }}": student_answer.strip()
    }
    
    for k, v in replacements.items():
        prompt = prompt.replace(k, str(v))

    provider = get_ai_provider()
    try:
        data = provider.generate_json(prompt=prompt)
    except Exception as e:
        logger.error(f"Error calling AI provider for answer evaluation: {e}. Falling back to MockProvider.")
        from .ai_providers.mock_provider import MockProvider
        data = MockProvider().generate_json(prompt=prompt)

    if not isinstance(data, dict) or "overall_score" not in data:
        from .ai_providers.mock_provider import MockProvider
        data = MockProvider().generate_json(prompt=prompt)

    score = int(data.get("overall_score", 70))
    clarity_score = int(data.get("clarity_score", score))
    technical_score = int(data.get("technical_score", score))
    completeness_score = int(data.get("completeness_score", score))
    relevance_score = int(data.get("relevance_score", score))
    
    feedback = data.get("summary_feedback", "Answer recorded.")
    good_points = data.get("good_points", [])
    missing_points = data.get("missing_points", [])
    correction = data.get("correction", "")
    follow_up = data.get("follow_up_question", "Can you elaborate on how you tested that module?")
    next_diff = data.get("next_difficulty", question.difficulty)

    answer_record = Answer(
        interview_id=interview.id,
        question_id=question.id,
        student_answer=student_answer.strip(),
        score=score,
        clarity_score=clarity_score,
        technical_score=technical_score,
        completeness_score=completeness_score,
        relevance_score=relevance_score,
        feedback=feedback,
        correction=correction,
        interviewer_followup=follow_up,
        difficulty_level=next_diff
    )
    answer_record.good_points = good_points
    answer_record.missing_points = missing_points

    db.session.add(answer_record)
    
    # Update interview progress
    interview.current_question_index += 1
    
    # Compute running average score
    answers = interview.answers.all() + [answer_record]
    total_scores = sum(a.score for a in answers)
    interview.overall_score = round(total_scores / len(answers), 1)

    db.session.commit()
    return answer_record
