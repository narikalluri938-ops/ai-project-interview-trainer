import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any
from app.models import db, Interview
from .ai_providers import get_ai_provider

logger = logging.getLogger(__name__)

PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"

def load_prompt_template(filename: str) -> str:
    path = PROMPTS_DIR / filename
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def generate_final_report(interview: Interview) -> Dict[str, Any]:
    """
    Synthesizes interview answers into a comprehensive readiness report
    with strengths, areas to improve, traps, revision topics, and study order.
    """
    project = interview.project
    answers = interview.answers.all()

    # Build QA transcript
    transcript_blocks = []
    for idx, ans in enumerate(answers, 1):
        q_text = ans.question.question if ans.question else "Question"
        transcript_blocks.append(
            f"Q{idx} [{ans.question.category if ans.question else 'general'}]: {q_text}\n"
            f"Student Answer: {ans.student_answer}\n"
            f"Score: {ans.score}/100 | Feedback: {ans.feedback}\n"
            f"Interviewer Follow-up: {ans.interviewer_followup}\n"
        )
    qa_transcripts = "\n---\n".join(transcript_blocks) if transcript_blocks else "No answers recorded."

    avg_score = interview.overall_score or 75.0

    template = load_prompt_template("report_generation.txt")
    prompt = template
    replacements = {
        "{{ project_name }}": project.name or "",
        "{{ technologies }}": project.technologies or "",
        "{{ role }}": project.role or "",
        "{{ total_questions }}": str(len(answers)),
        "{{ average_score }}": str(avg_score),
        "{{ qa_transcripts }}": qa_transcripts
    }

    for k, v in replacements.items():
        prompt = prompt.replace(k, str(v))

    provider = get_ai_provider()
    try:
        report_data = provider.generate_json(prompt=prompt)
    except Exception as e:
        logger.error(f"Error calling AI provider for report generation: {e}. Falling back to MockProvider.")
        from .ai_providers.mock_provider import MockProvider
        report_data = MockProvider().generate_json(prompt=prompt)

    if not isinstance(report_data, dict) or "readiness_score" not in report_data:
        from .ai_providers.mock_provider import MockProvider
        report_data = MockProvider().generate_json(prompt=prompt)

    # Save to interview
    interview.report = report_data
    interview.status = "completed"
    interview.completed_at = datetime.now(timezone.utc)
    db.session.commit()

    return report_data
