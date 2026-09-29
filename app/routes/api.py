from flask import Blueprint, jsonify, request
from app.models import db, Project

api_bp = Blueprint("api", __name__, url_prefix="/api")

SAMPLE_PROJECT = {
    "name": "Face Recognition Attendance System",
    "description": "An automated AI-driven attendance recording system that captures classroom or office video feeds, detects faces in real-time, matches them against registered student embeddings, and logs timestamped attendance into a relational database with duplicate-prevention constraints.",
    "technologies": "Python, OpenCV, Flask, MySQL, NumPy",
    "role": "Backend developer and face recognition module engineer",
    "features": "Real-time webcam frame processing, student registration with facial feature extraction, automatic attendance marking with timestamp and date, instructor dashboard to view attendance summaries and export CSV reports, duplicate entry prevention within the same class period.",
    "algorithms": "Haar Cascade / SSD for face detection, 128-dimensional deep face embeddings for recognition, Euclidean distance matching with 0.6 confidence threshold.",
    "database": "MySQL (tables: students, classes, attendance_logs with composite unique index on student_id and date).",
    "apis": "RESTful JSON endpoints in Flask: POST /api/register-face, POST /api/mark-attendance, GET /api/attendance-report.",
    "challenges": "Handling lighting variations in classroom conditions, avoiding false positives between similar-looking students, and optimizing frame processing rate to prevent UI lag on CPU.",
    "deployment": "Local demonstration on Flask WSGI with Gunicorn worker processes and MySQL service container.",
    "team_size": "2 developers (1 frontend/UI, 1 backend/AI)",
    "individual_contribution": "Designed and coded the entire Flask REST backend, integrated OpenCV detection pipeline, structured the MySQL database schema and transaction rollbacks, and wrote unit tests for the attendance logging logic.",
    "github_url": "https://github.com/example/face-recognition-attendance",
    "additional_notes": "Focused heavily on defensive database constraints and minimizing latency per frame."
}

@api_bp.route("/sample-project", methods=["GET"])
def get_sample_project():
    """Returns official demo project for 1-click testing."""
    return jsonify(SAMPLE_PROJECT)

@api_bp.route("/projects/<int:project_id>/stats", methods=["GET"])
def get_project_stats(project_id):
    project = db.session.get(Project, project_id)
    if not project:
        return jsonify({"error": "Project not found"}), 404
    return jsonify(project.prep_stats)
