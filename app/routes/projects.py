import logging
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, jsonify
from app.models import db, Project, Question
from app.services.project_analyzer import analyze_project
from app.services.question_generator import generate_questions_for_project

logger = logging.getLogger(__name__)
projects_bp = Blueprint("projects", __name__, url_prefix="/projects")

@projects_bp.route("/new", methods=["GET", "POST"])
def create_project():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip()
        technologies = request.form.get("technologies", "").strip()
        role = request.form.get("role", "").strip()

        # Validation of required fields
        if not name or not description or not technologies or not role:
            flash("Please provide at least Project Name, Description, Technologies, and your Role.", "danger")
            return render_template("project_form.html", form_data=request.form)

        # Input length constraints for security and stability
        if len(name) > 150:
            flash("Project name is too long (max 150 characters).", "warning")
            return render_template("project_form.html", form_data=request.form)
        if len(description) > 3000:
            flash("Description is too long (max 3000 characters).", "warning")
            return render_template("project_form.html", form_data=request.form)

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
                individual_contribution=request.form.get("individual_contribution", "").strip() or None,
                github_url=request.form.get("github_url", "").strip() or None,
                additional_notes=request.form.get("additional_notes", "").strip() or None,
            )
            db.session.add(project)
            db.session.commit()

            # Analyze project and generate questions
            try:
                analyze_project(project)
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
