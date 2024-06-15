from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from src.models import db

class Job(db.Model):
    """
    Represents a job in the organization.
    """
    __tablename__ = "jobs"
    id = Column(Integer, primary_key=True, index=True)
    job = Column(String, nullable=False, unique=True)

    employees = relationship("Employee", back_populates="job")
