import logging
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, jsonify
from app.models import db, Project, Interview, Question, Answer
from app.services.interview_evaluator import evaluate_student_answer
from app.services.report_generator import generate_final_report

logger = logging.getLogger(__name__)
interview_bp = Blueprint("interview", __name__, url_prefix="/interview")

@interview_bp.route("/start/<int:project_id>", methods=["POST"])
def start_interview(project_id):
    project = db.session.get(Project, project_id)
    if not project:
        abort(404)

    total_q = int(request.form.get("total_questions", 5))
    total_q = max(3, min(total_q, 10))

    interview = Interview(
        project_id=project.id,
        total_questions=total_q,
        current_question_index=0,
        status="in_progress"
    )
    db.session.add(interview)
    db.session.commit()

    return redirect(url_for("interview.session_view", interview_id=interview.id))

@interview_bp.route("/<int:interview_id>")
def session_view(interview_id):
    interview = db.session.get(Interview, interview_id)
    if not interview:
        abort(404)

    if interview.status == "completed":
        return redirect(url_for("interview.report_view", interview_id=interview.id))

    project = interview.project
    all_questions = project.questions.all()

    if not all_questions:
        from app.services.question_generator import generate_questions_for_project
        all_questions = generate_questions_for_project(project)

    answered_q_ids = [a.question_id for a in interview.answers.all()]
    unanswered = [q for q in all_questions if q.id not in answered_q_ids]

    # If all answered or reached total limit, finish interview
    if len(answered_q_ids) >= interview.total_questions or not unanswered:
        return redirect(url_for("interview.finish_interview", interview_id=interview.id))

    # Pick next question: alternate categories if possible
    current_q = unanswered[0]

    # Get last answer for immediate review if just submitted
    last_answer = interview.answers.order_by(Answer.id.desc()).first()

    return render_template(
        "mock_interview.html",
        interview=interview,
        project=project,
        question=current_q,
        question_number=len(answered_q_ids) + 1,
        last_answer=last_answer
    )

@interview_bp.route("/<int:interview_id>/submit", methods=["POST"])
def submit_answer(interview_id):
    interview = db.session.get(Interview, interview_id)
    if not interview:
        abort(404)

    question_id = request.form.get("question_id")
    student_answer = request.form.get("student_answer", "").strip()

    if not question_id or not student_answer:
        flash("Please provide an answer to continue.", "warning")
        return redirect(url_for("interview.session_view", interview_id=interview.id))

    question = db.session.get(Question, int(question_id))
    if not question:
        abort(404)

    answer_record = evaluate_student_answer(
        interview=interview,
        question=question,
        student_answer=student_answer
    )

    # Check if this was an AJAX request
    if request.headers.get("X-Requested-With") == "XMLHttpRequest" or request.is_json:
        return jsonify({
            "status": "success",
            "score": answer_record.score,
            "clarity_score": answer_record.clarity_score,
            "technical_score": answer_record.technical_score,
            "completeness_score": answer_record.completeness_score,
            "relevance_score": answer_record.relevance_score,
            "feedback": answer_record.feedback,
            "good_points": answer_record.good_points,
            "missing_points": answer_record.missing_points,
            "correction": answer_record.correction,
            "follow_up": answer_record.interviewer_followup,
            "next_url": url_for("interview.session_view", interview_id=interview.id)
        })

    flash("Answer evaluated! Review your feedback below.", "success")
    return redirect(url_for("interview.session_view", interview_id=interview.id))

@interview_bp.route("/<int:interview_id>/finish", methods=["GET", "POST"])
def finish_interview(interview_id):
    interview = db.session.get(Interview, interview_id)
    if not interview:
        abort(404)

    if not interview.report_json:
        generate_final_report(interview)

    return redirect(url_for("interview.report_view", interview_id=interview.id))

@interview_bp.route("/<int:interview_id>/report")
def report_view(interview_id):
    interview = db.session.get(Interview, interview_id)
    if not interview:
        abort(404)

    if not interview.report_json:
        generate_final_report(interview)

    project = interview.project
    answers = interview.answers.all()

    return render_template(
        "report.html",
        interview=interview,
        project=project,
        answers=answers,
        report=interview.report
    )
