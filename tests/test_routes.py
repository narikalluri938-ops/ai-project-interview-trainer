import pytest
from app.models import db, Project

def test_landing_page(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Turn Your Project Into Interview Confidence" in response.data
    assert b"Start Preparing" in response.data

def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json.get("status") == "healthy"

def test_sample_project_api(client):
    response = client.get("/api/sample-project")
    assert response.status_code == 200
    data = response.json
    assert data["name"] == "Face Recognition Attendance System"
    assert "Python" in data["technologies"]

def test_project_creation_and_redirect(client):
    response = client.post("/projects/new", data={
        "name": "Smart Campus Navigator",
        "description": "An indoor positioning Android & Flask app for university campuses.",
        "technologies": "Python, Flask, Kotlin, SQLite",
        "role": "Full Stack Developer",
        "features": "Pathfinding algorithm, campus map rendering"
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Smart Campus Navigator" in response.data
    assert b"Interview Readiness Progress" in response.data

def test_project_creation_validation_missing_required(client):
    response = client.post("/projects/new", data={
        "name": "",
        "description": "",
        "role": ""
    })
    assert response.status_code == 200
    assert b"Please provide at least Project Name, Description, and your Role / Contribution." in response.data

def test_short_3field_project_submission_and_inference(client):
    # Only 3 required fields submitted by user
    response = client.post("/projects/new", data={
        "name": "Smart Campus Navigator",
        "description": "An indoor positioning Android application and Flask backend for university campuses.",
        "role": "Lead Android & Backend Developer"
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Smart Campus Navigator" in response.data
    assert b"Auto-Extracted Stack" in response.data
    assert b"Confirmed from Input" in response.data
    assert b"Inferred / Likely" in response.data
    assert b"Must Verify" in response.data

    # Check project in DB
    project = Project.query.filter_by(name="Smart Campus Navigator").first()
    assert project is not None
    assert project.technologies is not None
    assert len(project.technologies) > 0
    assert "confirmed_details" in project.analysis
    assert "inferred_details" in project.analysis
    assert "items_to_verify" in project.analysis
    assert project.questions.count() >= 5

def test_404_error_page(client):
    response = client.get("/non-existent-page-xyz")
    assert response.status_code == 404
    assert b"Page Not Found" in response.data
