from datetime import datetime, timezone
from . import db

class Question(db.Model):
    __tablename__ = "questions"

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False)
    
    # Categories: 'basic', 'technical', 'why', 'scenario', 'follow_up'
    category = db.Column(db.String(50), nullable=False, default="technical")
    question = db.Column(db.Text, nullable=False)
    
    # Difficulty: 'beginner', 'intermediate', 'advanced', 'expert'
    difficulty = db.Column(db.String(20), nullable=False, default="intermediate")
    
    expected_concepts = db.Column(db.Text, nullable=True)
    interview_tips = db.Column(db.Text, nullable=True)
    tradeoffs = db.Column(db.Text, nullable=True)
    
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    answers = db.relationship("Answer", backref="question", cascade="all, delete-orphan", lazy="dynamic")

    @property
    def category_badge_class(self):
        badges = {
            "basic": "bg-primary",
            "technical": "bg-info text-dark",
            "why": "bg-warning text-dark",
            "scenario": "bg-purple text-white",
            "follow_up": "bg-secondary",
        }
        return badges.get(self.category, "bg-secondary")

    @property
    def difficulty_badge_class(self):
        badges = {
            "beginner": "bg-success",
            "intermediate": "bg-primary",
            "advanced": "bg-warning text-dark",
            "expert": "bg-danger",
        }
        return badges.get(self.difficulty, "bg-secondary")

    def __repr__(self):
        return f"<Question {self.id} [{self.category}]: {self.question[:40]}...>"
