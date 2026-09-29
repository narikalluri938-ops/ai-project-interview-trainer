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
        "technologies": "",
        "role": ""
    })
    assert response.status_code == 200
    assert b"Please provide at least Project Name, Description, Technologies, and your Role." in response.data

def test_404_error_page(client):
    response = client.get("/non-existent-page-xyz")
    assert response.status_code == 404
    assert b"Page Not Found" in response.data
