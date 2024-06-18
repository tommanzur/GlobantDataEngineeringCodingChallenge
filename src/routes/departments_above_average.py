from fastapi import APIRouter, HTTPException
from src.services.postgres_client import client

router = APIRouter()

@router.get("/departments_above_average/")
async def departments_above_average():
    """
    Get a list of departments whose performance
    is above the average.

    Returns:
        list: A list of departments above average performance.
    """
    try:
        response = await client.get_departments_above_average()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    return response
