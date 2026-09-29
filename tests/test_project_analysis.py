import pytest
from app.models import db, Project
from app.services.project_analyzer import analyze_project
from app.services.question_generator import generate_questions_for_project

def test_project_analysis_and_explanations(app, sample_project):
    with app.app_context():
        p = db.session.get(Project, sample_project.id)
        data = analyze_project(p)

        assert "explanations" in data
        assert "thirty_second" in data["explanations"]
        assert "one_minute" in data["explanations"]
        assert "two_minute" in data["explanations"]
        assert "technical" in data["explanations"]
        assert "simple" in data["explanations"]

        assert len(data["risk_areas"]) > 0
        assert len(data["learning_topics"]) > 0

        # Check property helpers on model
        assert len(p.explanations) == 5
        assert len(p.risk_areas) > 0
        assert len(p.learning_topics) > 0

def test_question_generation_categories(app, sample_project):
    with app.app_context():
        p = db.session.get(Project, sample_project.id)
        questions = generate_questions_for_project(p)

        assert len(questions) >= 5
        categories = {q.category for q in questions}

        assert "basic" in categories
        assert "technical" in categories
        assert "why" in categories
        assert "scenario" in categories

        for q in questions:
            assert q.question != ""
            assert q.difficulty in ["beginner", "intermediate", "advanced", "expert"]
