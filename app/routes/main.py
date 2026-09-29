from flask import Blueprint, render_template, jsonify
from app.models import Project

main_bp = Blueprint("main", __name__)

@main_bp.route("/")
def index():
    recent_projects = Project.query.order_by(Project.created_at.desc()).limit(5).all()
    return render_template("index.html", recent_projects=recent_projects)

@main_bp.route("/how-it-works")
def how_it_works():
    return render_template("index.html", scroll_to="how-it-works")

@main_bp.route("/health")
def health():
    return jsonify({"status": "healthy", "service": "AI Project Interview Trainer"}), 200
