import json
from datetime import datetime, timezone
from . import db

class Interview(db.Model):
    __tablename__ = "interviews"

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False)
    
    started_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at = db.Column(db.DateTime, nullable=True)
    
    # Status: 'in_progress', 'completed'
    status = db.Column(db.String(20), nullable=False, default="in_progress")
    total_questions = db.Column(db.Integer, default=5)
    current_question_index = db.Column(db.Integer, default=0)
    overall_score = db.Column(db.Float, default=0.0)
    
    # Final synthesized report JSON
    report_json = db.Column(db.Text, nullable=True)

    # Relationships
    answers = db.relationship("Answer", backref="interview", cascade="all, delete-orphan", lazy="dynamic", order_by="Answer.id")

    @property
    def report(self):
        if not self.report_json:
            return {}
        try:
            return json.loads(self.report_json)
        except Exception:
            return {}

    @report.setter
    def report(self, value):
        self.report_json = json.dumps(value) if value is not None else None

    @property
    def duration_minutes(self):
        if not self.completed_at or not self.started_at:
            return 0
        diff = self.completed_at - self.started_at
        return max(1, int(diff.total_seconds() / 60))

    def __repr__(self):
        return f"<Interview {self.id} (Project {self.project_id}) - {self.status}>"
