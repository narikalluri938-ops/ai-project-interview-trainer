import pytest
from app import create_app
from app.models import db, Project, Question, Interview, Answer

@pytest.fixture
def app():
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()

@pytest.fixture
def sample_project(app):
    with app.app_context():
        p = Project(
            name="Face Recognition Attendance System",
            description="An AI-based attendance recording system using camera feeds and embeddings.",
            technologies="Python, OpenCV, Flask, MySQL",
            role="Backend developer and face recognition module engineer",
            features="Real-time face detection, attendance logging",
            algorithms="Haar Cascades, 128-d deep embeddings",
            database="MySQL with students and attendance_logs tables"
        )
        db.session.add(p)
        db.session.commit()
        # Retrieve fresh with id
        return db.session.get(Project, p.id)
