import json
from datetime import datetime, timezone
from . import db

class Answer(db.Model):
    __tablename__ = "answers"

    id = db.Column(db.Integer, primary_key=True)
    interview_id = db.Column(db.Integer, db.ForeignKey("interviews.id"), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey("questions.id"), nullable=False)
    
    student_answer = db.Column(db.Text, nullable=False)
    
    # Scores (0-100)
    score = db.Column(db.Integer, default=0)
    clarity_score = db.Column(db.Integer, default=0)
    technical_score = db.Column(db.Integer, default=0)
    completeness_score = db.Column(db.Integer, default=0)
    relevance_score = db.Column(db.Integer, default=0)
    
    # Feedback fields
    feedback = db.Column(db.Text, nullable=True)
    good_points_json = db.Column(db.Text, nullable=True)
    missing_points_json = db.Column(db.Text, nullable=True)
    correction = db.Column(db.Text, nullable=True)
    
    # Follow-up question generated based on this answer
    interviewer_followup = db.Column(db.Text, nullable=True)
    difficulty_level = db.Column(db.String(20), default="intermediate")
    
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    @property
    def good_points(self):
        if not self.good_points_json:
            return []
        try:
            return json.loads(self.good_points_json)
        except Exception:
            return [self.good_points_json]

    @good_points.setter
    def good_points(self, value):
        self.good_points_json = json.dumps(value) if isinstance(value, list) else json.dumps([value])

    @property
    def missing_points(self):
        if not self.missing_points_json:
            return []
        try:
            return json.loads(self.missing_points_json)
        except Exception:
            return [self.missing_points_json]

    @missing_points.setter
    def missing_points(self, value):
        self.missing_points_json = json.dumps(value) if isinstance(value, list) else json.dumps([value])

    def __repr__(self):
        return f"<Answer {self.id} for Interview {self.interview_id}, Q {self.question_id}: score={self.score}>"
