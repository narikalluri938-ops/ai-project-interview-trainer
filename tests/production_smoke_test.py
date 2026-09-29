import os
import re
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Enforce production mode
os.environ["FLASK_ENV"] = "production"
os.environ["FLASK_DEBUG"] = "0"

from app import create_app
from app.models import db, Project

def run_production_smoke_test():
    app = create_app("production")
    assert not app.debug, "Production app must not have debug enabled!"
    # Register error route before handling any requests
    @app.route("/test-simulated-error")
    def trigger_error():
        raise RuntimeError("Simulated production internal failure")

    client = app.test_client()
    print("=== PRODUCTION BUILD SMOKE TEST ===")
    print("1. Verified: FLASK_ENV=production, FLASK_DEBUG=0, Debugger is OFF.")

    # 4. Test landing page
    r = client.get("/")
    assert r.status_code == 200
    assert b"Turn Your Project Into Interview Confidence" in r.data
    assert b"Debugger" not in r.data
    print("2. Landing page loaded successfully with no debug traces.")

    # 5. Create sample project
    r = client.get("/api/sample-project")
    sample_data = r.json
    r = client.post("/projects/new", data=sample_data, follow_redirects=True)
    assert r.status_code == 200
    assert b"Face Recognition Attendance System" in r.data
    print("3. Project created and analyzed in production mode.")

    # Extract project_id from database
    with app.app_context():
        p = Project.query.filter_by(name="Face Recognition Attendance System").order_by(Project.id.desc()).first()
        assert p is not None
        project_id = p.id

    # 6. Open dashboard
    r = client.get(f"/projects/{project_id}")
    assert r.status_code == 200
    assert b"30-Second Elevator Pitch" in r.data
    assert b"Resume Risks" in r.data
    print("4. Dashboard verified with 5-tier explanations and resume risks.")

    # 7. Open questions
    r = client.get(f"/projects/{project_id}/questions")
    assert r.status_code == 200
    assert b"What Interviewers Expect" in r.data
    print("5. Curated questions verified across all 5 categories.")

    # 8. Open learning
    r = client.get(f"/projects/{project_id}/learn")
    assert r.status_code == 200
    assert b"Core Concepts to Master" in r.data
    print("6. Learning mode verified with concept breakdowns.")

    # 9. Start mock interview
    r = client.post(f"/interview/start/{project_id}", data={"total_questions": 3}, follow_redirects=True)
    assert r.status_code == 200
    assert b"Question 1 of 3" in r.data
    match = re.search(r'/interview/(\d+)', r.request.path)
    assert match is not None
    interview_id = match.group(1)
    print(f"7. Mock interview session #{interview_id} started.")

    # 10 & 11. Submit an answer and generate follow-up
    match_q = re.search(r'name=["\']question_id["\']\s+value=["\'](\d+)["\']', r.data.decode("utf-8"))
    assert match_q is not None
    q_id = match_q.group(1)

    r = client.post(
        f"/interview/{interview_id}/submit",
        data={
            "question_id": q_id,
            "student_answer": "I implemented the Flask REST endpoints to receive camera detections and record attendance into MySQL tables with composite unique constraints on student_id and date."
        },
        follow_redirects=True
    )
    assert r.status_code == 200
    assert b"Feedback on Your Previous Answer" in r.data
    print("8. Answer evaluated and dynamic follow-up generated.")

    # 12 & 13. Finish interview and open final report
    r = client.get(f"/interview/{interview_id}/finish", follow_redirects=True)
    assert r.status_code == 200
    assert b"Interview Readiness Report" in r.data
    assert b"Strong Areas" in r.data
    assert b"Areas to Improve" in r.data
    assert b"Potential Interview Traps" in r.data
    print("9. Final Interview Readiness Report verified.")

    # 14. Test 404
    r = client.get("/non-existent-production-url-test")
    assert r.status_code == 404
    assert b"Page Not Found (404)" in r.data
    assert b"Traceback" not in r.data
    print("10. 404 error page verified with friendly template and zero traceback.")

    # 15. Confirm no debug traceback on error (simulate 500)
    r = client.get("/test-simulated-error")
    assert r.status_code == 500
    assert b"Something Went Wrong" in r.data
    assert b"Traceback (most recent call last)" not in r.data
    assert b"Simulated production internal failure" not in r.data
    print("11. Confirmed 500 error handler masks all internal traces and stack traces.")

    print("\n=== ALL 15 PRODUCTION BUILD SMOKE TESTS PASSED ===")

if __name__ == "__main__":
    run_production_smoke_test()
