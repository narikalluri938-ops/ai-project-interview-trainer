import logging
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, jsonify
from app.models import db, Project, Question
from app.services.project_analyzer import analyze_project
from app.services.question_generator import generate_questions_for_project

logger = logging.getLogger(__name__)
projects_bp = Blueprint("projects", __name__, url_prefix="/projects")

def infer_initial_technologies(name: str, description: str, role: str) -> str:
    """
    Infers likely technologies from name, description, and role
    when not explicitly supplied by the user.
    """
    text = f"{name} {description} {role}".lower()
    detected = []

    tech_patterns = [
        ("Python", ["python", "py", "django", "flask", "fastapi", "numpy", "pandas", "pytorch", "tensorflow", "opencv", "scikit"]),
        ("OpenCV", ["opencv", "computer vision", "face recognition", "facial", "image processing", "webcam"]),
        ("Flask", ["flask", "wsgi"]),
        ("Django", ["django"]),
        ("FastAPI", ["fastapi"]),
        ("PyTorch", ["pytorch", "torch"]),
        ("TensorFlow", ["tensorflow", "keras"]),
        ("CNN", ["cnn", "convolutional", "resnet", "vgg", "yolo", "deep learning", "neural network"]),
        ("Java", ["java", "spring", "springboot", "spring boot", "hibernate"]),
        ("Spring Boot", ["spring boot", "springboot"]),
        ("Node.js", ["node.js", "nodejs", "node", "express"]),
        ("React", ["react", "react.js", "reactjs", "next.js", "nextjs"]),
        ("Android", ["android", "kotlin", "java android"]),
        ("Go", ["golang", "go language", "goroutine"]),
        ("C++", ["c++", "cpp"]),
        ("PostgreSQL", ["postgres", "postgresql"]),
        ("MySQL", ["mysql"]),
        ("SQLite", ["sqlite"]),
        ("MongoDB", ["mongo", "mongodb", "nosql"]),
        ("Redis", ["redis", "cache"]),
        ("Docker", ["docker", "container"]),
        ("AWS", ["aws", "s3", "ec2", "lambda"]),
        ("REST API", ["rest", "api", "endpoints", "json"]),
    ]

    for label, keywords in tech_patterns:
        if any(kw in text for kw in keywords):
            if label not in detected:
                detected.append(label)

    # Domain fallbacks if no specific keywords were matched
    if not detected:
        if any(k in text for k in ["face", "vision", "camera", "detect", "attendance"]):
            detected = ["Python", "OpenCV", "Flask", "MySQL"]
        elif any(k in text for k in ["ml", "ai", "model", "predict", "classifier", "scan", "tumor"]):
            detected = ["Python", "PyTorch", "Flask", "Docker"]
        elif any(k in text for k in ["shop", "ecommerce", "cart", "store", "payment"]):
            detected = ["JavaScript", "Node.js", "Express", "MongoDB"]
        elif any(k in text for k in ["mobile", "app", "gps", "campus", "map"]):
            detected = ["Kotlin", "Android SDK", "REST API", "SQLite"]
        elif any(k in text for k in ["bank", "account", "transaction", "fintech"]):
            detected = ["Java", "Spring Boot", "PostgreSQL", "Docker"]
        else:
            detected = ["Python", "REST API", "Relational Database"]

    return ", ".join(detected)

@projects_bp.route("/new", methods=["GET", "POST"])
def create_project():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip()
        role = request.form.get("role", "").strip()
        technologies = request.form.get("technologies", "").strip()

        # Validation of the 3 required fields
        if not name or not description or not role:
            flash("Please provide at least Project Name, Description, and your Role / Contribution.", "danger")
            return render_template("project_form.html", form_data=request.form)

        # Input length constraints for security and stability
        if len(name) > 150:
            flash("Project name is too long (max 150 characters).", "warning")
            return render_template("project_form.html", form_data=request.form)
        if len(description) > 3000:
            flash("Description is too long (max 3000 characters).", "warning")
            return render_template("project_form.html", form_data=request.form)

        # Auto-infer technologies if not provided
        if not technologies:
            technologies = infer_initial_technologies(name, description, role)

        try:
            project = Project(
                name=name,
                description=description,
                technologies=technologies,
                role=role,
                features=request.form.get("features", "").strip() or None,
                algorithms=request.form.get("algorithms", "").strip() or None,
                database=request.form.get("database", "").strip() or None,
                apis=request.form.get("apis", "").strip() or None,
                challenges=request.form.get("challenges", "").strip() or None,
                deployment=request.form.get("deployment", "").strip() or None,
                team_size=request.form.get("team_size", "").strip() or None,
                individual_contribution=request.form.get("individual_contribution", "").strip() or role,
                github_url=request.form.get("github_url", "").strip() or None,
                additional_notes=request.form.get("additional_notes", "").strip() or None,
            )
            db.session.add(project)
            db.session.commit()

            # Analyze project and generate questions
            try:
                analysis_data = analyze_project(project)
                # If analysis inferred more specific technologies and user didn't enter them, update
                inferred_techs = analysis_data.get("inferred_details", {}).get("technologies") or analysis_data.get("inferred_technologies")
                if inferred_techs and not request.form.get("technologies"):
                    if isinstance(inferred_techs, list):
                        project.technologies = ", ".join(inferred_techs)
                    elif isinstance(inferred_techs, str):
                        project.technologies = inferred_techs
                    db.session.commit()

                generate_questions_for_project(project)
            except Exception as e:
                logger.error(f"Analysis warning for project {project.id}: {e}")
                # Project is still saved; user can view dashboard

            flash(f"Project '{project.name}' successfully analyzed! Let's prepare for your interview.", "success")
            return redirect(url_for("projects.dashboard", project_id=project.id))

        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to create project: {e}")
            flash("An error occurred while saving your project. Please try again.", "danger")
            return render_template("project_form.html", form_data=request.form)

    return render_template("project_form.html", form_data={})

@projects_bp.route("/<int:project_id>")
def dashboard(project_id):
    project = db.session.get(Project, project_id)
    if not project:
        abort(404)

    # Ensure analysis and questions are generated if missing
    if not project.analysis_json:
        analyze_project(project)
    if project.questions.count() == 0:
        generate_questions_for_project(project)

    stats = project.prep_stats
    return render_template("dashboard.html", project=project, stats=stats)

@projects_bp.route("/<int:project_id>/questions")
def questions_view(project_id):
    project = db.session.get(Project, project_id)
    if not project:
        abort(404)

    category = request.args.get("category", "all")
    difficulty = request.args.get("difficulty", "all")

    query = project.questions
    if category != "all":
        query = query.filter_by(category=category)
    if difficulty != "all":
        query = query.filter_by(difficulty=difficulty)

    questions_list = query.all()
    categories = ["basic", "technical", "why", "scenario", "follow_up"]

    return render_template(
        "questions.html",
        project=project,
        questions=questions_list,
        current_category=category,
        current_difficulty=difficulty,
        categories=categories
    )

@projects_bp.route("/<int:project_id>/learn")
def learn_view(project_id):
    project = db.session.get(Project, project_id)
    if not project:
        abort(404)

    topics = project.learning_topics
    return render_template("learn.html", project=project, topics=topics)

@projects_bp.route("/<int:project_id>/risks")
def risks_view(project_id):
    project = db.session.get(Project, project_id)
    if not project:
        abort(404)

    risks = project.risk_areas
    return render_template("risks.html", project=project, risks=risks)

@projects_bp.route("/<int:project_id>/regenerate", methods=["POST"])
def regenerate(project_id):
    project = db.session.get(Project, project_id)
    if not project:
        abort(404)

    action = request.form.get("action", "all")
    if action in ["analysis", "all"]:
        analyze_project(project)
    if action in ["questions", "all"]:
        generate_questions_for_project(project, force_regenerate=True)

    flash("Interview prep materials refreshed with latest analysis!", "info")
    return redirect(url_for("projects.dashboard", project_id=project.id))
