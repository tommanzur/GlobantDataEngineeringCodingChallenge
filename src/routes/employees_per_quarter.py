from fastapi import APIRouter
from src.services.postgres_client import client

router = APIRouter()

@router.get("/employees_per_quarter/")
async def employees_per_quarter():
    """
    Retrieve the number of employees per quarter from the database.
    
    Returns:
        JSON response containing the number of employees per quarter.
    """
    response = await client.get_employees_per_quarter()
    return response
