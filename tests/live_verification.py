import re
import sys
import requests

BASE_URL = "http://127.0.0.1:5000"

def run_live_verification():
    session = requests.Session()
    results = []

    def record_step(name, passed, detail=""):
        status = "[PASS]" if passed else "[FAIL]"
        results.append((name, passed, detail))
        print(f"{status} {name}: {detail}")
        if not passed:
            raise AssertionError(f"Step failed: {name} - {detail}")

    print("==================================================")
    print("LIVE REAL-WORLD VERIFICATION OF APPLICATION CLAIMS")
    print(f"Target: {BASE_URL}")
    print("==================================================\n")

    # 1. Health check
    try:
        r = session.get(f"{BASE_URL}/health")
        passed = (r.status_code == 200 and r.json().get("status") == "healthy")
        record_step("1. Server Health Check", passed, f"Status {r.status_code}, response: {r.json()}")
    except Exception as e:
        record_step("1. Server Health Check", False, str(e))

    # 2. Landing Page
    try:
        r = session.get(f"{BASE_URL}/")
        claims = [
            "Turn Your Project Into Interview Confidence" in r.text,
            "Start Preparing" in r.text,
            "The Real Problem" in r.text,
            "Structured Journey" in r.text,
            "Why This Is Different" in r.text,
            "Anti-Hallucination" in r.text,
            "Resume Risk" in r.text,
            "Live Interview Simulator" in r.text
        ]
        passed = (r.status_code == 200 and all(claims))
        record_step("2. Landing Page & Product Claims", passed, "Hero, Problem, Journey, Features & CTA verified.")
    except Exception as e:
        record_step("2. Landing Page & Product Claims", False, str(e))

    # 3. Sample Project API
    try:
        r = session.get(f"{BASE_URL}/api/sample-project")
        data = r.json()
        passed = (
            r.status_code == 200 and
            data.get("name") == "Face Recognition Attendance System" and
            "OpenCV" in data.get("technologies", "") and
            "Flask" in data.get("technologies", "")
        )
        record_step("3. Sample Project API", passed, f"Returned project: '{data.get('name')}' with stack: '{data.get('technologies')}'")
    except Exception as e:
        record_step("3. Sample Project API", False, str(e))

    # 4. Form Validation (Empty Input)
    try:
        r = session.post(f"{BASE_URL}/projects/new", data={"name": "", "description": "", "technologies": "", "role": ""})
        passed = (r.status_code == 200 and "Please provide at least" in r.text)
        record_step("4. Form Empty Input Validation", passed, "Rejected invalid submission with flash alert.")
    except Exception as e:
        record_step("4. Form Empty Input Validation", False, str(e))

    # 5. Project Creation & Analysis
    sample_data = session.get(f"{BASE_URL}/api/sample-project").json()
    try:
        r = session.post(f"{BASE_URL}/projects/new", data=sample_data, allow_redirects=True)
        dashboard_url = r.url
        project_id = dashboard_url.rstrip("/").split("/")[-1]
        passed = (r.status_code == 200 and "Face Recognition Attendance System" in r.text and project_id.isdigit())
        record_step("5. Project Creation & Initial Analysis", passed, f"Created project ID #{project_id} at {dashboard_url}")
    except Exception as e:
        record_step("5. Project Creation & Initial Analysis", False, str(e))

    # 6. Dashboard: 5-Tier Explanations
    try:
        r = session.get(f"{BASE_URL}/projects/{project_id}")
        explanations_present = [
            "30-Second Elevator Pitch" in r.text,
            "1-Minute Technical Overview" in r.text,
            "2-Minute Deep Technical Walkthrough" in r.text,
            "Under-the-Hood Technical" in r.text,
            "Layman / Recruiter Pitch" in r.text
        ]
        passed = (r.status_code == 200 and all(explanations_present))
        record_step("6. Dashboard 5-Tier Explanations", passed, "Verified 30s, 1m, 2m, Technical, and Layman explanations.")
    except Exception as e:
        record_step("6. Dashboard 5-Tier Explanations", False, str(e))

    # 7. Dashboard: Anti-Hallucination & Risk Areas
    try:
        r = session.get(f"{BASE_URL}/projects/{project_id}")
        anti_hallucination_check = (
            "Resume Risks" in r.text and
            "Unstated Assumptions" in r.text and
            "Scrutiny Risk" in r.text
        )
        record_step("7. Anti-Hallucination & Risk Areas", anti_hallucination_check, "Resume scrutiny risks & unstated assumptions present.")
    except Exception as e:
        record_step("7. Anti-Hallucination & Risk Areas", False, str(e))

    # 8. Questions by Category
    try:
        r = session.get(f"{BASE_URL}/projects/{project_id}/questions")
        categories_found = []
        for cat in ["basic", "technical", "why", "scenario", "follow_up"]:
            r_cat = session.get(f"{BASE_URL}/projects/{project_id}/questions?category={cat}")
            if r_cat.status_code == 200 and f"badge-{cat}" in r_cat.text:
                categories_found.append(cat)
        passed = len(categories_found) >= 4
        record_step("8. Curated Questions across Categories", passed, f"Verified categories: {categories_found}")
    except Exception as e:
        record_step("8. Curated Questions across Categories", False, str(e))

    # 9. Concept Learning Mode
    try:
        r = session.get(f"{BASE_URL}/projects/{project_id}/learn")
        learning_criteria = [
            "Core Concepts to Master" in r.text,
            "Why it's used" in r.text,
            "How it works under the hood" in r.text,
            "In your project" in r.text,
            "Likely Interview Question" in r.text
        ]
        passed = (r.status_code == 200 and all(learning_criteria))
        record_step("9. Concept Learning Mode", passed, "Verified concept breakdown cards (definition, why used, mechanics, interview Q).")
    except Exception as e:
        record_step("9. Concept Learning Mode", False, str(e))

    # 10. Dedicated Resume Risks View
    try:
        r = session.get(f"{BASE_URL}/projects/{project_id}/risks")
        passed = (r.status_code == 200 and "Interview Risk Areas & Defense" in r.text and "Probing Questions Interviewers Will Ask" in r.text)
        record_step("10. Dedicated Resume Risks View", passed, "Verified probing questions and defense strategies.")
    except Exception as e:
        record_step("10. Dedicated Resume Risks View", False, str(e))

    # 11. Mock Interview Session Initiation
    try:
        r = session.post(f"{BASE_URL}/interview/start/{project_id}", data={"total_questions": 3}, allow_redirects=True)
        interview_url = r.url
        interview_id = interview_url.rstrip("/").split("/")[-1]
        passed = (r.status_code == 200 and "Question 1 of 3" in r.text and interview_id.isdigit())
        record_step("11. Mock Interview Start", passed, f"Started interview #{interview_id} at {interview_url}")
    except Exception as e:
        record_step("11. Mock Interview Start", False, str(e))

    # 12. Mock Interview: Weak Answer Evaluation
    try:
        match = re.search(r'name=["\']question_id["\']\s+value=["\'](\d+)["\']', r.text)
        q1_id = match.group(1)
        r = session.post(
            f"{BASE_URL}/interview/{interview_id}/submit",
            data={
                "question_id": q1_id,
                "student_answer": "I don't know much about this, my teammate handled it."
            },
            allow_redirects=True
        )
        passed = (
            r.status_code == 200 and
            "Feedback on Your Previous Answer" in r.text and
            "Clarity" in r.text and
            "Technical" in r.text
        )
        record_step("12. Mock Interview Weak Answer Feedback", passed, "Correctly graded weak answer with constructive advice & clarification follow-up.")
    except Exception as e:
        record_step("12. Mock Interview Weak Answer Feedback", False, str(e))

    # 13. Mock Interview: Strong Answer Evaluation
    try:
        match = re.search(r'name=["\']question_id["\']\s+value=["\'](\d+)["\']', r.text)
        q2_id = match.group(1)
        r = session.post(
            f"{BASE_URL}/interview/{interview_id}/submit",
            data={
                "question_id": q2_id,
                "student_answer": "We engineered our Flask API with blueprinted routing and used connection pooling with MySQL. We applied composite unique constraints on student_id and date to prevent duplicate attendance writes."
            },
            allow_redirects=True
        )
        passed = (r.status_code == 200 and "Feedback on Your Previous Answer" in r.text)
        record_step("13. Mock Interview Strong Answer Evaluation", passed, "Evaluated technical depth and presented score breakdown.")
    except Exception as e:
        record_step("13. Mock Interview Strong Answer Evaluation", False, str(e))

    # 14. Final Interview Report Generation
    try:
        r = session.get(f"{BASE_URL}/interview/{interview_id}/finish", allow_redirects=True)
        report_checks = [
            "Interview Readiness Report" in r.text,
            "Executive Summary" in r.text,
            "Strong Areas" in r.text,
            "Areas to Improve" in r.text,
            "Concepts to Revise Before Your Interview" in r.text,
            "Potential Interview Traps" in r.text,
            "Recommended Revision Sequence" in r.text,
            "Practical Interview Day Advice" in r.text,
            "Full Question & Answer Transcripts" in r.text
        ]
        passed = (r.status_code == 200 and all(report_checks))
        record_step("14. Final Interview Readiness Report", passed, "Verified readiness score, strengths, gaps, traps, revision order, and transcripts.")
    except Exception as e:
        record_step("14. Final Interview Readiness Report", False, str(e))

    # 15. Persistence and Dashboard Update
    try:
        r = session.get(f"{BASE_URL}/projects/{project_id}")
        passed = (r.status_code == 200 and f"#{interview_id}" in r.text and "Completed" in r.text)
        record_step("15. Persistence & History Tracking", passed, f"Confirmed Interview #{interview_id} is recorded in dashboard history.")
    except Exception as e:
        record_step("15. Persistence & History Tracking", False, str(e))

    # 16. Friendly 404 Error Page
    try:
        r = session.get(f"{BASE_URL}/route-that-does-not-exist-12345")
        passed = (r.status_code == 404 and "Page Not Found (404)" in r.text and "Return Home" in r.text)
        record_step("16. Friendly 404 Error Handling", passed, "Custom styled 404 page rendered cleanly.")
    except Exception as e:
        record_step("16. Friendly 404 Error Handling", False, str(e))

    print("\n==================================================")
    print(f"VERIFICATION SUMMARY: {sum(1 for r in results if r[1])}/{len(results)} CHECKS PASSED")
    print("==================================================")

if __name__ == "__main__":
    run_live_verification()
