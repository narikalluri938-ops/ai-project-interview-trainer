import json
from datetime import datetime, timezone
from . import db

class Project(db.Model):
    __tablename__ = "projects"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    technologies = db.Column(db.String(300), nullable=True)
    role = db.Column(db.String(200), nullable=False)
    
    # Optional fields
    features = db.Column(db.Text, nullable=True)
    algorithms = db.Column(db.Text, nullable=True)
    database = db.Column(db.String(150), nullable=True)
    apis = db.Column(db.String(250), nullable=True)
    challenges = db.Column(db.Text, nullable=True)
    deployment = db.Column(db.String(200), nullable=True)
    team_size = db.Column(db.String(50), nullable=True)
    individual_contribution = db.Column(db.Text, nullable=True)
    github_url = db.Column(db.String(250), nullable=True)
    additional_notes = db.Column(db.Text, nullable=True)
    
    # Cached AI Analysis
    analysis_json = db.Column(db.Text, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    questions = db.relationship("Question", backref="project", cascade="all, delete-orphan", lazy="dynamic")
    interviews = db.relationship("Interview", backref="project", cascade="all, delete-orphan", lazy="dynamic")

    @property
    def analysis(self):
        if not self.analysis_json:
            return {}
        try:
            return json.loads(self.analysis_json)
        except Exception:
            return {}

    @analysis.setter
    def analysis(self, value):
        self.analysis_json = json.dumps(value) if value is not None else None

    @property
    def explanations(self):
        return self.analysis.get("explanations", {})

    @property
    def risk_areas(self):
        return self.analysis.get("risk_areas", [])

    @property
    def learning_topics(self):
        return self.analysis.get("learning_topics", [])

    @property
    def confirmed_details(self):
        return self.analysis.get("confirmed_details", {
            "name": self.name,
            "description": self.description,
            "role": self.role
        })

    @property
    def inferred_details(self):
        return self.analysis.get("inferred_details", {})

    @property
    def items_to_verify(self):
        return self.analysis.get("items_to_verify", self.analysis.get("unstated_assumptions", []))

    @property
    def prep_stats(self):
        total_questions = self.questions.count()
        total_interviews = self.interviews.count()
        completed_interviews = self.interviews.filter_by(status="completed").count()
        
        # Calculate answered questions count across all interviews
        from .answer import Answer
        from .interview import Interview
        answered_q_ids = db.session.query(Answer.question_id).join(Interview).filter(
            Interview.project_id == self.id
        ).distinct().count()

        # Calculate readiness percentage
        if total_questions == 0:
            readiness = 0
        else:
            readiness = min(100, int((answered_q_ids / max(1, total_questions)) * 60 + (completed_interviews * 20)))

        return {
            "total_questions": total_questions,
            "answered_questions": answered_q_ids,
            "total_interviews": total_interviews,
            "completed_interviews": completed_interviews,
            "readiness_percent": readiness,
            "learning_topics_count": len(self.learning_topics),
            "risk_areas_count": len(self.risk_areas)
        }

    @property
    def recent_interviews(self):
        from .interview import Interview
        return self.interviews.order_by(Interview.id.desc()).all()

    def __repr__(self):
        return f"<Project {self.id}: {self.name}>"
