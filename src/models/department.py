from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from src.models import db

class Department(db.Model):
    """
    Represents a department within the organization.
    """
    __tablename__ = "departments"
    id = Column(Integer, primary_key=True, index=True)
    department = Column(String, nullable=False, unique=True)

    employees = relationship("Employee", back_populates="department")
