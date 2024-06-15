from unittest.mock import AsyncMock
from io import BytesIO
import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport
from src.main import app
from src.models.tables import TableName


@pytest.fixture(scope="module")
def client():
    """Fixture to create a TestClient instance for testing FastAPI endpoints."""
    with TestClient(app) as c:
        yield c


@pytest.fixture
def mock_db_client(mocker):
    """Fixture to mock the database client for testing purposes."""
    mock = mocker.patch(
        "src.services.postgres_client.client.handle_upload", new_callable=AsyncMock
    )
    return mock


def create_upload_file(file_content: str, filename: str = "test.csv"):
    """Helper function to create a file tuple for testing file uploads."""
    file = BytesIO(file_content.encode())
    return (filename, file, "text/csv")


@pytest.mark.asyncio
async def test_upload_csv_employee(client: TestClient, mock_db_client):
    """Test uploading a CSV file to the employee table."""
    file_content = (
        "1,Juan Pérez,2023-06-15 08:00:00,1,1\n2,María Gómez,2023-06-15 09:00:00,2,2\n"
    )
    upload_file = create_upload_file(file_content)
    mock_db_client.return_value = {
        "success": True,
        "message": "File uploaded successfully",
    }

    files = {"file": upload_file}

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as ac:
        response = await ac.post(
            "/upload_csv/", files=files, params={"table": TableName.EMPLOYEE.value}
        )

    assert response.status_code == 200
    assert response.json() == {"success": True, "message": "File uploaded successfully"}


@pytest.mark.asyncio
async def test_upload_csv_invalid_table(client: TestClient, mock_db_client):
    """Test uploading a CSV file to an invalid table."""
    file_content = "1,Invalid Data\n"
    upload_file = create_upload_file(file_content)
    mock_db_client.side_effect = Exception("Invalid table")

    files = {"file": upload_file}

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as ac:
        response = await ac.post(
            "/upload_csv/", files=files, params={"table": "INVALID"}
        )

    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "loc": ["query", "table"],
                "msg": "value is not a valid enumeration member; permitted: 'employee', 'job', 'department'",
                "type": "type_error.enum",
            }
        ]
    }


@pytest.mark.asyncio
async def test_upload_csv_job(client: TestClient, mock_db_client):
    """Test uploading a CSV file to the job table."""
    file_content = "1,Desarrollador\n2,Analista\n"
    upload_file = create_upload_file(file_content)
    mock_db_client.return_value = {
        "success": True,
        "message": "File uploaded successfully",
    }

    files = {"file": upload_file}

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as ac:
        response = await ac.post(
            "/upload_csv/", files=files, params={"table": TableName.JOB.value}
        )

    assert response.status_code == 200
    assert response.json() == {"success": True, "message": "File uploaded successfully"}


@pytest.mark.asyncio
async def test_upload_csv_department(client: TestClient, mock_db_client):
    """Test uploading a CSV file to the department table."""
    file_content = "1,Recursos Humanos\n2,Tecnología\n"
    upload_file = create_upload_file(file_content)
    mock_db_client.return_value = {
        "success": True,
        "message": "File uploaded successfully",
    }

    files = {"file": upload_file}

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as ac:
        response = await ac.post(
            "/upload_csv/", files=files, params={"table": TableName.DEPARTMENT.value}
        )

    assert response.status_code == 200
    assert response.json() == {"success": True, "message": "File uploaded successfully"}
