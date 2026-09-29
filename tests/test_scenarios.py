import pytest
from app.models import db, Project
from app.services.project_analyzer import analyze_project
from app.services.question_generator import generate_questions_for_project
from app.services.interview_evaluator import evaluate_student_answer
from app.services.ai_providers.mock_provider import MockProvider

def test_ml_project_analysis(app):
    with app.app_context():
        p = Project(
            name="Brain Tumor Classification Using CNN",
            description="Deep learning system using convolutional neural networks to classify MRI scans as glioma, meningioma, or pituitary tumor.",
            technologies="Python, PyTorch, CNN, ResNet50, Flask, Docker",
            role="Machine Learning Engineer",
            algorithms="ResNet50 transfer learning, Adam optimizer, CrossEntropyLoss",
            database="None"
        )
        db.session.add(p)
        db.session.commit()

        analysis = analyze_project(p)
        assert len(analysis["risk_areas"]) > 0
        assert "explanations" in analysis

        questions = generate_questions_for_project(p)
        assert len(questions) >= 5
        q_texts = " ".join([q.question for q in questions])
        assert any(k in q_texts.lower() for k in ["cnn", "model", "python", "algorithm", "dataset", "accuracy", "train"])

def test_java_web_project_analysis(app):
    with app.app_context():
        p = Project(
            name="Banking Transaction Portal",
            description="Core banking web application handling concurrent deposits, withdrawals, and account audit logs.",
            technologies="Java, Spring Boot, PostgreSQL, Hibernate, Docker",
            role="Backend Developer",
            database="PostgreSQL with accounts and transactions tables"
        )
        db.session.add(p)
        db.session.commit()

        analysis = analyze_project(p)
        assert "thirty_second" in analysis["explanations"]

        questions = generate_questions_for_project(p)
        categories = {q.category for q in questions}
        assert "technical" in categories
        assert "why" in categories

def test_project_with_no_database(app):
    with app.app_context():
        p = Project(
            name="Distributed CLI Log Parser",
            description="Command-line utility in Go that parses gigabyte-sized log files using goroutines and regex.",
            technologies="Go, RegEx, Concurrency",
            role="Systems Engineer",
            database=None
        )
        db.session.add(p)
        db.session.commit()

        analysis = analyze_project(p)
        assert analysis is not None
        assert "explanations" in analysis

        questions = generate_questions_for_project(p)
        assert len(questions) > 0

def test_ai_provider_graceful_fallback_on_exception(app, monkeypatch):
    """Verifies that if an AI provider raises an exception, the system gracefully falls back to MockProvider without crashing."""
    from app.services import project_analyzer

    class FailingProvider:
        def generate_json(self, *args, **kwargs):
            raise ConnectionError("Simulated API network outage or invalid API key")

    monkeypatch.setattr(project_analyzer, "get_ai_provider", lambda: FailingProvider())

    with app.app_context():
        p = Project(
            name="IoT Weather Station",
            description="Embedded sensor monitor sending telemetry over MQTT.",
            technologies="C++, ESP32, MQTT",
            role="Firmware Engineer"
        )
        db.session.add(p)
        db.session.commit()

        # Should NOT raise an unhandled exception; falls back gracefully
        analysis = analyze_project(p)
        assert "explanations" in analysis
        assert "thirty_second" in analysis["explanations"]
