import pytest
from app.models import db, Project, Question, Interview
from app.services.interview_evaluator import evaluate_student_answer
from app.services.report_generator import generate_final_report

def test_answer_evaluation_and_scoring(app, sample_project):
    with app.app_context():
        p = db.session.get(Project, sample_project.id)
        q = Question(
            project_id=p.id,
            category="technical",
            question="Why did you choose Flask over Django?",
            difficulty="intermediate"
        )
        db.session.add(q)
        db.session.commit()

        iv = Interview(project_id=p.id, total_questions=3)
        db.session.add(iv)
        db.session.commit()

        # Test evaluating strong answer
        ans = evaluate_student_answer(
            interview=iv,
            question=q,
            student_answer="I chose Flask because our project is an API-first microservice for face verification. We required a lightweight WSGI framework with zero ORM overhead to minimize request response latency."
        )

        assert ans.id is not None
        assert ans.score >= 70
        assert ans.clarity_score > 0
        assert ans.technical_score > 0
        assert ans.interviewer_followup != ""
        assert iv.current_question_index == 1

def test_final_report_generation(app, sample_project):
    with app.app_context():
        p = db.session.get(Project, sample_project.id)
        q = Question(
            project_id=p.id,
            category="basic",
            question="Tell me about your project."
        )
        db.session.add(q)
        db.session.commit()

        iv = Interview(project_id=p.id, total_questions=1)
        db.session.add(iv)
        db.session.commit()

        evaluate_student_answer(
            interview=iv,
            question=q,
            student_answer="It is a face recognition attendance system built with OpenCV and Flask to automate student attendance tracking."
        )

        report = generate_final_report(iv)
        assert "readiness_score" in report
        assert "strong_areas" in report
        assert "areas_to_improve" in report
        assert "preparation_order" in report
        assert iv.status == "completed"
