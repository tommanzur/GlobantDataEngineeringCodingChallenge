from enum import Enum

class TableName(str, Enum):
    """
    Enum representing the possible table names in the database.
    """
    JOB = "job"
    EMPLOYEE = "employee"
    DEPARTMENT = "department"
