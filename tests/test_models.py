import pytest
from app.models import db, Project, Question, Interview, Answer

def test_project_model_creation(app):
    with app.app_context():
        p = Project(
            name="E-Commerce API",
            description="A microservices backend for online shopping.",
            technologies="Node.js, Express, MongoDB, Redis",
            role="Backend Engineer"
        )
        db.session.add(p)
        db.session.commit()

        assert p.id is not None
        assert p.name == "E-Commerce API"
        assert p.analysis == {}
        assert p.explanations == {}
        assert p.risk_areas == []
        assert p.learning_topics == []
        assert repr(p) == f"<Project {p.id}: E-Commerce API>"

def test_question_model(app, sample_project):
    with app.app_context():
        q = Question(
            project_id=sample_project.id,
            category="technical",
            question="How does Flask route HTTP requests?",
            difficulty="intermediate",
            expected_concepts="Routing table, WSGI dispatch"
        )
        db.session.add(q)
        db.session.commit()

        assert q.id is not None
        assert q.category_badge_class == "bg-info text-dark"
        assert q.difficulty_badge_class == "bg-primary"
        assert "Flask" in repr(q)

def test_interview_and_answer_lifecycle(app, sample_project):
    with app.app_context():
        q = Question(
            project_id=sample_project.id,
            category="technical",
            question="Why did you choose MySQL?",
            difficulty="intermediate"
        )
        db.session.add(q)
        db.session.commit()

        iv = Interview(
            project_id=sample_project.id,
            total_questions=5,
            status="in_progress"
        )
        db.session.add(iv)
        db.session.commit()

        ans = Answer(
            interview_id=iv.id,
            question_id=q.id,
            student_answer="We chose MySQL for ACID guarantees and relational structure.",
            score=85,
            clarity_score=80,
            technical_score=90
        )
        ans.good_points = ["Mentioned ACID", "Clear relational rationale"]
        ans.missing_points = ["Did not mention indexing"]
        db.session.add(ans)
        db.session.commit()

        assert ans.id is not None
        assert len(ans.good_points) == 2
        assert len(ans.missing_points) == 1
        assert iv.answers.count() == 1
