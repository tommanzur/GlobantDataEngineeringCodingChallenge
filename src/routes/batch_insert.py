from io import StringIO
import pandas as pd
from fastapi import APIRouter, UploadFile, File, HTTPException
from src.services.postgres_client import client
from src.models.tables import TableName


router = APIRouter()


@router.post("/batch_insert/")
async def batch_insert(table: TableName, file: UploadFile = File(...)):
    """
    Endpoint for batch inserting data into the specified table.

    Args:
        table (TableName): The name of the table to insert data into.
        file (UploadFile): The CSV file containing data to be inserted.

    Returns:
        dict: A response indicating the result of the batch insert operation.

    Raises:
        HTTPException: If an error occurs during the batch insert process.
    """
    try:
        contents = await file.read()
        column_names = get_column_names(table)

        df = pd.read_csv(StringIO(contents.decode("utf-8")), header=None, names=column_names)
        rows = df.to_dict(orient='records')

        response = await client.handle_batch_insert(rows=rows, table=table.value)
        return response
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

def get_column_names(table: TableName) -> list:
    """
    Get the column names for the specified table.

    Args:
        table (TableName): The name of the table.

    Returns:
        list: A list of column names for the specified table.

    Raises:
        HTTPException: If the table name is invalid.
    """
    if table == TableName.EMPLOYEE:
        return ['id', 'name', 'datetime', 'department_id', 'job_id']
    elif table == TableName.JOB:
        return ['id', 'job']
    elif table == TableName.DEPARTMENT:
        return ['id', 'department']
    else:
        raise HTTPException(status_code=400, detail="Invalid table name")
