from fastapi import APIRouter, UploadFile, File, HTTPException
from src.services.postgres_client import client
from src.models.tables import TableName

router = APIRouter()


@router.post("/upload_csv/")
async def upload_csv(table: TableName, file: UploadFile = File(...)):
    """
    Endpoint to upload a CSV file to a specified table in the database.

    Args:
        table (TableName): The name of the table where the CSV data will be uploaded.
        file (UploadFile): The CSV file to be uploaded.

    Returns:
        Response from the database client indicating the success or failure of the upload.

    Raises:
        HTTPException: If there is an error processing the file upload.
    """
    try:
        response = await client.handle_upload(file, table.value)
        return response
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
