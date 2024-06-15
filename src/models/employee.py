from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from src.models import db

class Employee(db.Model):
    """
    Represents an employee in the organization.
    """
    __tablename__ = "employees"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    datetime = Column(DateTime, nullable=True)
    department_id = Column(Integer, ForeignKey('departments.id'), nullable=True)
    job_id = Column(Integer, ForeignKey('jobs.id'), nullable=True)

    department = relationship("Department", back_populates="employees")
    job = relationship("Job", back_populates="employees")
