from fastapi import APIRouter, HTTPException
from src.services.postgres_client import client

router = APIRouter()

@router.get("/employees_per_quarter/")
async def employees_per_quarter():
    """
    Retrieve the number of employees per quarter from the database.
    
    Returns:
        JSON response containing the number of employees per quarter.
    """
    try:
        response = await client.get_employees_per_quarter()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    return response
