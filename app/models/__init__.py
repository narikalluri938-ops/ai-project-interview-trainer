from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .project import Project
from .question import Question
from .interview import Interview
from .answer import Answer

__all__ = ["db", "Project", "Question", "Interview", "Answer"]
