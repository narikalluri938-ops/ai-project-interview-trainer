import re
import json
import logging
from typing import Dict, Any, Optional
from .base import AIProvider

logger = logging.getLogger(__name__)

class MockProvider(AIProvider):
    """
    Intelligent heuristic-based AI provider.
    Runs 100% offline with zero external API dependencies, perfectly suited
    for out-of-the-box local testing, offline demos, and test suites.
    """

    def generate_completion(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        json_mode: bool = True,
        max_tokens: int = 2500,
        temperature: float = 0.7
    ) -> str:
        prompt_lower = prompt.lower()

        # Identify which prompt is being triggered using unique header anchors
        if "interview preparation & readiness report" in prompt_lower or "qa_transcripts" in prompt_lower or "readiness report for a student" in prompt_lower:
            return json.dumps(self._mock_report_generation(prompt), indent=2)
        elif "evaluating a candidate's response" in prompt_lower or "evaluation guidelines" in prompt_lower:
            return json.dumps(self._mock_answer_evaluation(prompt), indent=2)
        elif "question categories to generate" in prompt_lower or "generate realistic, project-specific interview questions" in prompt_lower:
            return json.dumps(self._mock_question_generation(prompt), indent=2)
        elif "generate a sharp, realistic follow-up question" in prompt_lower:
            return json.dumps(self._mock_followup_generation(prompt), indent=2)
        elif "analyze the following student project" in prompt_lower:
            return json.dumps(self._mock_project_analysis(prompt), indent=2)
        else:
            return json.dumps({"status": "success", "message": "Standard analysis response generated."}, indent=2)

    def _extract_field(self, prompt: str, field_name: str) -> str:
        marker = f"{field_name}:"
        for line in prompt.splitlines():
            if line.strip().startswith(marker):
                return line.split(marker, 1)[1].strip()
        return ""

    def _mock_project_analysis(self, prompt: str) -> Dict[str, Any]:
        name = self._extract_field(prompt, "Project Name") or "Technical Project"
        role = self._extract_field(prompt, "Role") or "Software Engineer"
        tech = self._extract_field(prompt, "Technologies") or ""
        desc = self._extract_field(prompt, "Description") or "A software application."
        features = self._extract_field(prompt, "Features") or ""
        database = self._extract_field(prompt, "Database") or ""

        # Auto-infer tech and database if not explicitly stated
        if not tech or tech == "Not specified":
            text_corpus = f"{name} {desc} {role}".lower()
            if any(k in text_corpus for k in ["opencv", "face", "vision", "camera", "image"]):
                tech = "Python, OpenCV, Flask, MySQL, NumPy"
                database = "MySQL"
            elif any(k in text_corpus for k in ["cnn", "tumor", "mri", "pytorch", "resnet"]):
                tech = "Python, PyTorch, CNN, ResNet50, Docker"
                database = "None"
            elif any(k in text_corpus for k in ["java", "spring", "bank"]):
                tech = "Java, Spring Boot, PostgreSQL, Docker"
                database = "PostgreSQL"
            elif any(k in text_corpus for k in ["go", "log", "cli", "parser"]):
                tech = "Go, RegEx, Concurrency, CLI"
                database = "None"
            elif any(k in text_corpus for k in ["android", "kotlin", "navigator", "campus"]):
                tech = "Kotlin, Android SDK, Flask, SQLite"
                database = "SQLite"
            elif any(k in text_corpus for k in ["shop", "ecommerce", "cart"]):
                tech = "JavaScript, Node.js, Express, MongoDB"
                database = "MongoDB"
            else:
                tech = "Python, Flask, Relational Database, REST API"
                database = "Relational Database"

        tech_list = [t.strip() for t in tech.split(",") if t.strip()]
        tech_lower = tech.lower()
        has_cv = any(k in tech_lower for k in ["opencv", "face", "vision", "image", "cnn"])
        has_flask = "flask" in tech_lower
        has_sql = any(k in tech_lower for k in ["sql", "mysql", "postgres", "sqlite"])

        thirty_sec = (
            f"I built '{name}', {desc.rstrip('.')} using {tech}. "
            f"My primary focus was {role}, where I designed the data pipeline, integrated core modules, "
            f"and ensured accurate, automated processing."
        )

        one_min = (
            f"During placements, I worked on '{name}' to solve manual inefficiencies in tracking and verification. "
            f"The core stack comprises {tech}. In my role as {role}, I implemented the core workflows, "
            f"structured the {database if database else 'database'} schemas, and connected the backend service endpoints. "
            f"One key hurdle was balancing real-time execution latency with accuracy, which we resolved by optimizing "
            f"the processing pipeline and caching active records."
        )

        two_min = (
            f"'{name}' is a technical solution engineered to automate verification and record keeping. "
            f"Traditional methods rely on manual logging, which introduces delays and human error. "
            f"Our architecture separates client capture from server processing. The backend is built with {tech}. "
            f"Specifically for my contribution in {role}: I engineered the request validation pipeline, "
            f"integrated the detection/processing logic, and implemented structured storage in {database if database else 'the database'}. "
            f"During testing, we faced race conditions and latency spikes when processing concurrent requests. "
            f"I resolved this by indexing frequent lookup fields and introducing input rate limiting. "
            f"If I were to rebuild this for 100,000 users, I would decouple the ingestion layer with an asynchronous message queue."
        )

        technical_exp = (
            f"Architecturally, '{name}' follows a layered modular pattern. Input requests are validated via {tech_list[0] if tech_list else 'REST'} "
            f"controllers before passing data to the business logic layer. For storage, {database if database else 'relational tables'} "
            f"maintain entity relationships with foreign key integrity. If external models or services are invoked, "
            f"pre-processing normalizes input dimensions before computation to prevent runtime memory bloat."
        )

        simple_exp = (
            f"Imagine having to manually check and write down attendance or records for dozens of people every single day. "
            f"'{name}' completely automates this process using technology: it recognizes the input, verifies who it is, "
            f"and records everything safely into a database in seconds without any paper or manual work."
        )

        # Build risk areas
        risks = []
        if has_cv:
            risks.append({
                "claim": "Computer Vision / Face Recognition module listed",
                "risk_reason": "Interviewers will check whether you trained a deep model from scratch or merely used pre-trained Haar Cascades / dlib embeddings.",
                "probing_questions": [
                    "Did you train the face recognition model, or use a pre-trained library like OpenCV / FaceNet?",
                    "How does your system handle lighting variation, occlusions, and duplicate frame detections?"
                ],
                "recommendation": "Clearly state on your resume: 'Implemented real-time face detection utilizing pre-trained Haar Cascades/FaceNet and mapped embeddings to a MySQL student registry'."
            })

        if has_flask:
            risks.append({
                "claim": "Flask Backend framework",
                "risk_reason": "Interviewers will ask why Flask was chosen over FastAPI or Django, and how WSGI servers like Gunicorn differ from 'flask run'.",
                "probing_questions": [
                    "Why did you choose Flask over Django or FastAPI?",
                    "How does Flask handle concurrent requests, and what is the difference between Flask's built-in dev server and a production WSGI server?"
                ],
                "recommendation": "Be ready to explain Flask's lightweight WSGI design and how you structured blueprints and database connections."
            })

        if has_sql:
            risks.append({
                "claim": f"{database if database else 'SQL'} Database Schema",
                "risk_reason": "Interviewers frequently ask about primary keys, indexes, and preventing duplicate or dirty reads.",
                "probing_questions": [
                    "What tables did you create, and what are their primary and foreign keys?",
                    "How did you prevent duplicate records if the same person is detected twice within a minute?"
                ],
                "recommendation": "Sketch out your table schema beforehand: student_id, timestamp, status, with composite indexes on (student_id, date)."
            })

        # Learning topics
        learning_topics = [
            {
                "topic": "Real-Time Pipeline Optimization" if has_cv else "Request Lifecycle & Middleware",
                "definition": "Technique for managing incoming streaming data or web requests without blocking worker threads.",
                "why_used": "To maintain low latency and prevent application freezing under concurrent client loads.",
                "how_it_works": "Decouples resource-intensive compute from the primary I/O thread using batching or worker pools.",
                "how_it_appears_in_project": f"In '{name}', handling user data efficiently before persisting to {database if database else 'the database'}.",
                "concrete_example": "Processing frames at reduced resolution (e.g. 640x480) or utilizing connection pooling.",
                "interview_question": "How did you ensure the system remained responsive when processing input data?",
                "follow_up_question": "What profiling tool did you use to measure the bottleneck?"
            },
            {
                "topic": "Database Normalization & ACID Transactions",
                "definition": "Database principles ensuring relational tables minimize redundancy and guarantee transaction consistency.",
                "why_used": "Prevents data anomalies, duplicate records, and incomplete updates during system crashes.",
                "how_it_works": "Splits data into logical entities (3NF) and binds multi-step updates into atomic BEGIN...COMMIT blocks.",
                "how_it_appears_in_project": f"Recording attendance or user transactions in {database if database else 'relational tables'} without race conditions.",
                "concrete_example": "Wrapping timestamp and student status insertion in an atomic transaction.",
                "interview_question": f"How is your {database if database else 'SQL'} schema structured to prevent duplicate entries on the same day?",
                "follow_up_question": "What isolation level does your database use, and could a phantom read occur?"
            },
            {
                "topic": "API Design & REST Conventions",
                "definition": "Architectural standard using HTTP verbs (GET, POST, PUT, DELETE) and status codes (200, 201, 400, 404, 500).",
                "why_used": "Provides predictable, decoupled communication between frontends, capture devices, and the backend.",
                "how_it_works": "Client sends payload in JSON format with appropriate headers; server routes, validates, and responds with status codes.",
                "how_it_appears_in_project": f"Endpoints in {tech} that receive user commands and return status notifications.",
                "concrete_example": "POST /api/attendance with payload {'student_id': 101, 'timestamp': '2026-09-29T10:00:00'}.",
                "interview_question": "What HTTP status codes do your endpoints return on success versus duplicate detection?",
                "follow_up_question": "How do you validate the request payload before hitting your database?"
            }
        ]

        confirmed_details = {
            "project_name": name,
            "problem_statement": desc,
            "candidate_role": role,
            "explicit_contributions": role
        }

        inferred_details = {
            "technologies": tech_list,
            "architecture": f"Client Interface -> Backend Service ({tech_list[0] if tech_list else 'REST API'}) -> {database if database and database != 'Not specified' else 'Relational Storage'}",
            "database": database if database and database != "Not specified" else ("MySQL / PostgreSQL relational database" if has_sql or not has_cv else "SQLite / Local relational storage"),
            "features": [
                f"Core automated processing workflow for {name}",
                "Input sanitization, parameter validation, and boundary checks",
                "Persistent status and record tracking with queryable history"
            ],
            "algorithms": (
                ["Haar Cascades / SSD face detection", "128-d deep facial embeddings with Euclidean distance"] if has_cv else
                ["Convolutional feature extraction", "CrossEntropyLoss with gradient optimization"] if "cnn" in tech_lower else
                ["B-Tree primary/foreign key indexing", "Atomic transaction isolation (ACID)"]
            ),
            "apis": [
                "RESTful HTTP endpoints for data submission and query retrieval",
                "JSON payload request/response serialization with HTTP status codes"
            ],
            "challenges": [
                "Handling concurrent request latency and database write race conditions",
                "Balancing processing overhead with real-time response targets",
                "Ensuring graceful error handling when inputs are malformed or missing"
            ]
        }

        items_to_verify = [
            f"Confirm the exact database engine and schema design (e.g. {database if database else 'MySQL/PostgreSQL'}) you actually used.",
            "Verify whether third-party models or packages were pre-trained or trained by you from scratch.",
            "Prepare your explanation of authentication, authorization, and error handling.",
            "Clarify your hosting and deployment setup (local WSGI, Docker container, or cloud VM) if asked."
        ]

        return {
            "project_summary": f"'{name}' is a project built with {tech} to solve {desc.rstrip('.')}.",
            "objective": f"Automate tracking and verification with reliable data persistence.",
            "problem_solved": desc,
            "architecture_summary": f"Client Capture Layer -> Backend API ({tech_list[0] if tech_list else 'Backend'}) -> Storage ({database if database else 'Database'}).",
            "confirmed_details": confirmed_details,
            "inferred_details": inferred_details,
            "items_to_verify": items_to_verify,
            "inferred_technologies": tech_list,
            "explanations": {
                "thirty_second": thirty_sec,
                "one_minute": one_min,
                "two_minute": two_min,
                "technical": technical_exp,
                "simple": simple_exp
            },
            "risk_areas": risks,
            "learning_topics": learning_topics,
            "unstated_assumptions": [
                "Your project details do not specify production server deployment (e.g. Nginx, Gunicorn, Docker). An interviewer may ask how you would host this live.",
                "Your details do not explicitly clarify authentication and security policies for administrative access. Prepare to explain role-based access control."
            ]
        }

    def _mock_question_generation(self, prompt: str) -> Dict[str, Any]:
        name = self._extract_field(prompt, "Project Name") or "this project"
        tech = self._extract_field(prompt, "Technologies") or ""
        database = self._extract_field(prompt, "Database") or ""
        role = self._extract_field(prompt, "Role") or "Backend Developer"
        desc = self._extract_field(prompt, "Description") or ""

        # Auto-infer stack if not provided in prompt
        if not tech or tech == "Not specified":
            text_corpus = f"{name} {desc} {role} {prompt}".lower()
            if any(k in text_corpus for k in ["opencv", "face", "vision", "camera"]):
                tech = "Python, OpenCV, Flask, MySQL, NumPy"
                database = "MySQL"
            elif any(k in text_corpus for k in ["cnn", "tumor", "mri", "pytorch"]):
                tech = "Python, PyTorch, CNN, ResNet50, Docker"
            elif any(k in text_corpus for k in ["java", "spring"]):
                tech = "Java, Spring Boot, PostgreSQL, Docker"
                database = "PostgreSQL"
            elif any(k in text_corpus for k in ["go", "log"]):
                tech = "Go, RegEx, Concurrency, CLI"
            elif any(k in text_corpus for k in ["android", "kotlin", "navigator"]):
                tech = "Kotlin, Android SDK, Flask, SQLite"
                database = "SQLite"
            else:
                tech = "Python, Flask, SQL"
                database = "relational database"

        tech_lower = tech.lower()

        questions = [
            # Basic Questions
            {
                "category": "basic",
                "question": f"Can you give me a high-level overview of '{name}' and what problem it solves?",
                "difficulty": "beginner",
                "expected_concepts": "Problem statement, core workflow, target users, high-level stack",
                "interview_tips": "Use the STAR method: Situation, Task, Action, Result. Keep it under 90 seconds.",
                "tradeoffs": "Automated pipeline vs manual paper/spreadsheet tracking."
            },
            {
                "category": "basic",
                "question": f"What was your specific individual role as '{role}' in this project?",
                "difficulty": "beginner",
                "expected_concepts": "Individual modules owned, API development, integration, testing",
                "interview_tips": "Be honest about team boundaries. Say 'I specifically owned X, while my teammate handled Y'.",
                "tradeoffs": "Solo architecture decisions vs collaborative team task division."
            },
            {
                "category": "basic",
                "question": "What was the most challenging technical bug you encountered while building this, and how did you resolve it?",
                "difficulty": "intermediate",
                "expected_concepts": "Root cause analysis, debugging steps, tools used (logs, profilers, breakpoints), outcome",
                "interview_tips": "Pick a real technical bug (e.g. race condition, encoding error, memory leak) rather than a trivial typo.",
                "tradeoffs": "Quick monkey patch vs proper architectural fix."
            },

            # Technical Questions
            {
                "category": "technical",
                "question": f"In your {tech} stack, how is your project directory structured and how do modules communicate?",
                "difficulty": "intermediate",
                "expected_concepts": "Modular architecture, blueprints/controllers, separation of concerns, service layer",
                "interview_tips": "Describe how separation of concerns makes your codebase maintainable and testable.",
                "tradeoffs": "Single monolithic file vs modular blueprinted structure."
            },
            {
                "category": "technical",
                "question": f"How do you handle database connections and schema design in {database}?",
                "difficulty": "intermediate",
                "expected_concepts": "Connection pooling, foreign key constraints, indexes, ORM vs raw SQL queries",
                "interview_tips": "Mention primary keys, indexing frequently searched fields, and closing connections.",
                "tradeoffs": "ORM convenience vs raw SQL query performance."
            },
            {
                "category": "technical",
                "question": f"If an unhandled exception occurs in your backend during processing, how is it caught and communicated back?",
                "difficulty": "advanced",
                "expected_concepts": "Try/except blocks, global error handlers, HTTP 500 status codes, structured JSON error payloads, logging",
                "interview_tips": "Explain why returning stack traces to clients is a security vulnerability.",
                "tradeoffs": "Detailed debug errors in development vs sanitized error payloads in production."
            },

            # Why Questions
            {
                "category": "why",
                "question": f"Why did you choose {tech.split(',')[0].strip()} instead of alternative languages or frameworks?",
                "difficulty": "intermediate",
                "expected_concepts": "Library ecosystem, development velocity, ease of prototyping, team familiarity",
                "interview_tips": "Acknowledge the alternative objectively. Don't claim your choice is universally superior.",
                "tradeoffs": "Development speed vs raw execution speed / concurrency models."
            },
            {
                "category": "why",
                "question": f"Why did you select {database} rather than a NoSQL document database like MongoDB?",
                "difficulty": "intermediate",
                "expected_concepts": "Structured tabular data, ACID compliance, relational integrity, predictable queries",
                "interview_tips": "Explain how relationships (e.g. students to attendance records) naturally fit relational foreign keys.",
                "tradeoffs": "Relational strict schema & ACID vs NoSQL flexible schema & horizontal partitioning."
            },
            {
                "category": "why",
                "question": "What technical trade-offs did you make between execution speed, system complexity, and accuracy?",
                "difficulty": "advanced",
                "expected_concepts": "Processing resolution, batch intervals, database write frequency, resource utilization",
                "interview_tips": "Demonstrate mature engineering thinking by showing you weighed costs before deciding.",
                "tradeoffs": "Real-time instant processing with higher CPU vs queued batch processing with slight delay."
            },

            # Scenario Questions
            {
                "category": "scenario",
                "question": f"Your application runs fine with 50 test records, but in a real college with 10,000 students it slows down significantly. What would you investigate first?",
                "difficulty": "advanced",
                "expected_concepts": "Database indexes, slow query logs, N+1 query problems, connection pool exhaustion, CPU profiling",
                "interview_tips": "Follow a methodical diagnostic order: frontend latency -> network -> application compute -> database query plans.",
                "tradeoffs": "Vertical scaling (more RAM/CPU) vs horizontal scaling with read replicas and caching."
            },
            {
                "category": "scenario",
                "question": f"The {database} crashes or loses network connectivity right when a record is being written. How does your system handle this?",
                "difficulty": "advanced",
                "expected_concepts": "Database transactions, rollback mechanisms, retry queues, local disk buffering, graceful client failure",
                "interview_tips": "Describe how atomic transactions prevent half-written records and how retry logic works.",
                "tradeoffs": "Failing fast to user vs buffering in local SQLite/Redis buffer for background synchronization."
            },
            {
                "category": "scenario",
                "question": "An interviewer suspects your project was copied from an online tutorial. How do you prove your authentic understanding?",
                "difficulty": "expert",
                "expected_concepts": "Deep knowledge of edge cases, line-by-line understanding, custom features added, lessons learned",
                "interview_tips": "Offer to walk through the exact architecture, explain trade-offs you wrestled with, and describe bugs you solved.",
                "tradeoffs": "Using boilerplate starter code vs building understanding from scratch."
            },

            # Follow-up Questions
            {
                "category": "follow_up",
                "question": "You mentioned this system is automated. What happens if invalid or corrupted data is submitted to your API?",
                "difficulty": "intermediate",
                "expected_concepts": "Schema validation, sanitization, HTTP 400 Bad Request, rejection logs",
                "interview_tips": "Demonstrate defense-in-depth: never trust client input.",
                "tradeoffs": "Strict rejection vs permissive type-coercion."
            },
            {
                "category": "follow_up",
                "question": "How would you secure this system if we wanted to deploy it on a public domain today?",
                "difficulty": "advanced",
                "expected_concepts": "HTTPS/TLS, JWT or Session authentication, CORS policy, rate limiting, SQL injection protection",
                "interview_tips": "List the standard OWASP checklist: authentication, authorization, encrypted transit, sanitized queries.",
                "tradeoffs": "Open development convenience vs production security hardening."
            }
        ]

        if "opencv" in tech_lower or "face" in tech_lower or "cnn" in tech_lower:
            questions.append({
                "category": "technical",
                "question": "How does the facial detection and recognition pipeline work under the hood? What exact algorithm extracts the facial features?",
                "difficulty": "advanced",
                "expected_concepts": "Bounding box detection, feature extraction, 128-d or 512-d embeddings, Euclidean distance / cosine similarity",
                "interview_tips": "Clearly distinguish detection (finding a face in an image) from recognition (matching that face to a known identity).",
                "tradeoffs": "Haar Cascades (fast CPU, low accuracy) vs Deep CNNs / FaceNet (accurate, GPU intensive)."
            })
            questions.append({
                "category": "scenario",
                "question": "Two students look somewhat similar or lighting changes drastically, causing a false positive. How would you debug and mitigate this?",
                "difficulty": "expert",
                "expected_concepts": "Confidence threshold tuning, histogram equalization for lighting, multi-frame consensus, liveness detection",
                "interview_tips": "Explain that setting a stricter similarity threshold reduces false acceptances, even if it slightly increases false rejections.",
                "tradeoffs": "False Acceptance Rate (FAR) vs False Rejection Rate (FRR) calibration."
            })

        return {"questions": questions}

    def _mock_answer_evaluation(self, prompt: str) -> Dict[str, Any]:
        student_ans = ""
        pattern = r"Candidate's Answer:\s*\"\"\"([\s\S]*?)\"\"\""
        match = re.search(pattern, prompt, re.IGNORECASE)
        if match:
            student_ans = match.group(1).strip()
        else:
            for line in prompt.splitlines():
                if "Candidate's Answer:" in line:
                    idx = prompt.find("Candidate's Answer:")
                    student_ans = prompt[idx:].replace("Candidate's Answer:", "").strip()
                    break

        ans_lower = student_ans.lower()
        word_count = len(student_ans.split())

        has_tech_substance = any(
            kw in ans_lower
            for kw in [
                "because", "api", "architecture", "framework", "database", "latency",
                "scale", "index", "wsgi", "orm", "algorithm", "model", "pipeline",
                "trade-off", "overhead", "microservice", "query", "endpoint", "transaction"
            ]
        )

        # Determine scoring based on depth and technical substance
        if word_count < 8 or "don't know" in ans_lower or "not sure" in ans_lower:
            overall = 35
            clarity = 50
            tech_score = 30
            completeness = 25
            relevance = 40
            feedback = "The answer is too brief or evasive. In a technical interview, avoid saying just 'I don't know' without offering your reasoning or how you would approach solving it."
            good = ["Honest acknowledgment instead of making up false information."]
            missing = ["Explanation of underlying mechanism", "Specific architectural or code details", "Handling of edge cases"]
            correction = "Always explain the thought process: 'While I didn't directly configure X, here is how I understand the flow and how I would implement it...'"
            next_diff = "beginner"
            follow_up = "Let's take a step back: what is the fundamental purpose of this component in your project?"
        elif has_tech_substance and word_count >= 18:
            overall = 85
            clarity = 85
            tech_score = 88
            completeness = 80
            relevance = 90
            feedback = "Strong technical explanation! You articulated the problem, the specific technology chosen, and demonstrated hands-on familiarity with the workflow."
            good = ["Clear structured communication", "Referenced actual technical mechanics", "Demonstrated project ownership"]
            missing = ["Could mention real-world failure scenarios or performance metrics", "Could discuss what alternative solutions were evaluated"]
            correction = "To elevate this to an offer-winning answer, quantify your results (e.g. 'reduced latency by 30%', 'handles 50 FPS')."
            next_diff = "advanced"
            follow_up = "That makes sense. Now, how would your approach change if your data volume or concurrent users increased tenfold?"
        elif word_count < 25:
            overall = 65
            clarity = 70
            tech_score = 60
            completeness = 55
            relevance = 75
            feedback = "You have the right intuition and stated the basic concept, but the answer lacks technical depth and concrete implementation details from your codebase."
            good = ["Identified the core purpose correctly", "Kept the explanation concise"]
            missing = ["Underlying libraries or algorithms used", "Specific trade-offs considered", "How errors or scale are managed"]
            correction = "Back up high-level statements with concrete mechanics. If you say 'it is lightweight', explain what makes it lightweight (e.g. microframework, unopinionated routing, minimal overhead)."
            next_diff = "intermediate"
            follow_up = "You mentioned that concept. Can you explain specifically how that was implemented in your code?"
        else:
            overall = 80
            clarity = 80
            tech_score = 80
            completeness = 75
            relevance = 85
            feedback = "Solid answer! You provided a good overview of the concept and connected it to your project."
            good = ["Good structured explanation", "Addressed the main question"]
            missing = ["Could be even more specific with architectural trade-offs"]
            correction = "Always highlight the trade-offs between chosen technologies and alternatives."
            next_diff = "intermediate"
            follow_up = "What alternatives did you consider before settling on this?"

        return {
            "overall_score": overall,
            "clarity_score": clarity,
            "technical_score": tech_score,
            "completeness_score": completeness,
            "relevance_score": relevance,
            "summary_feedback": feedback,
            "good_points": good,
            "missing_points": missing,
            "correction": correction,
            "interviewer_perspective": "The interviewer is assessing whether you truly wrote the code and understand the architectural trade-offs.",
            "next_difficulty": next_diff,
            "follow_up_question": follow_up
        }

    def _mock_followup_generation(self, prompt: str) -> Dict[str, Any]:
        return {
            "follow_up_question": "What specific bottlenecks did that approach solve in your project, and how did you verify it?",
            "reasoning": "Probing whether candidate has verified performance or is repeating theoretical claims.",
            "expected_key_points": ["Measurement metrics", "Profiling tools or log timestamps", "Concrete before-and-after outcome"],
            "difficulty": "intermediate"
        }

    def _mock_report_generation(self, prompt: str) -> Dict[str, Any]:
        return {
            "readiness_score": 82,
            "readiness_verdict": "Interview Ready with Focused Polishing",
            "readiness_summary": "You demonstrated solid ownership of your core project workflow and clear communication on high-level architecture. To reach top-tier interview readiness, deepen your mastery of edge cases, database transaction isolation, and scalability limits.",
            "strong_areas": [
                "Project Objective & Problem Framing",
                "Clarity on Individual Contribution",
                "Core Technology Stack Fundamentals"
            ],
            "areas_to_improve": [
                "Handling Edge Cases and Failure Modes",
                "Database Indexing & Concurrent Transaction Guarantees",
                "Quantifying Performance Trade-offs (latency, memory, accuracy)"
            ],
            "struggled_questions": [
                {
                    "question": "How does your system handle database failure or latency spikes during processing?",
                    "why_struggled": "Focused only on the happy path without defensive engineering safeguards.",
                    "ideal_direction": "Discuss atomic transactions, rollback strategies, and retry queues."
                }
            ],
            "concepts_to_revise": [
                {
                    "concept": "Database Indexing & Composite Keys",
                    "priority": "High",
                    "revision_guide": "Understand B-Trees, primary key clustered indexes, and composite indexes on (user_id, date)."
                },
                {
                    "concept": "WSGI vs Development Server",
                    "priority": "Medium",
                    "revision_guide": "Know why 'flask run' is single-threaded and how Gunicorn manages worker processes."
                },
                {
                    "concept": "RESTful Error Handling & Status Codes",
                    "priority": "Medium",
                    "revision_guide": "Review HTTP 400 (Bad Request), 404 (Not Found), 409 (Conflict), and 500 (Internal Server Error)."
                }
            ],
            "interview_traps": [
                {
                    "trap_claim": "Listing multiple advanced models or frameworks without clarifying whether pre-trained or built from scratch",
                    "danger": "Interviewer will grill you on gradient descent, loss functions, or mathematical backprop.",
                    "defense_strategy": "Clarify immediately: 'We integrated pre-trained weights for feature extraction and engineered the business logic layer around it.'"
                },
                {
                    "trap_claim": "Claiming the project is 'fully scalable' without load testing numbers",
                    "danger": "Interviewer will ask for specific QPS (queries per second) or concurrent user thresholds.",
                    "defense_strategy": "Say: 'In our testing environment, it processed single-user requests within 200ms; to scale to thousands, we would need connection pooling and caching.'"
                }
            ],
            "preparation_order": [
                "Step 1: Rehearse your 1-minute project pitch until it sounds natural and confident.",
                "Step 2: Draw the end-to-end architecture on a whiteboard, tracing data from client to database.",
                "Step 3: Review database table structures, primary keys, and foreign keys.",
                "Step 4: Practice answering the 3 tricky scenario questions generated in this trainer."
            ],
            "final_advice": "Technical interviewers care far more about honest engineering understanding, trade-off awareness, and debugging skills than memorized textbook definitions. Speak with conviction about what you built, acknowledge boundaries gracefully, and walk through your problem-solving process."
        }
