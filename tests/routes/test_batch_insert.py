import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport
from src.main import app
from src.models.tables import TableName
from unittest.mock import AsyncMock


@pytest.fixture(scope="module")
def client():
    """Fixture to create a TestClient instance for testing FastAPI endpoints."""
    with TestClient(app) as c:
        yield c


@pytest.fixture
def mock_db_client(mocker):
    """Fixture to mock the database client for testing purposes."""
    mock = mocker.patch(
        "src.services.postgres_client.client.handle_batch_insert",
        new_callable=AsyncMock,
    )
    return mock


@pytest.mark.asyncio
async def test_batch_insert_employee(client: TestClient, mock_db_client):
    """Test batch inserting employee data using a CSV file."""
    data = (
        "1,Juan Pérez,2023-06-15 08:00:00,1,1\n"
        "2,María Gómez,2023-06-15 09:00:00,2,2\n"
    )
    files = {"file": ("test.csv", data, "text/csv")}
    mock_db_client.return_value = {"success": True, "rows_inserted": 2}

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as ac:
        response = await ac.post(
            "/batch_insert/", files=files, params={"table": TableName.EMPLOYEE.value}
        )

    assert response.status_code == 200
    assert response.json() == {"success": True, "rows_inserted": 2}


@pytest.mark.asyncio
async def test_batch_insert_invalid_table(client: TestClient, mock_db_client):
    """Test batch inserting data into an invalid table."""
    data = "1,Invalid Data\n"
    files = {"file": ("test.csv", data, "text/csv")}

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as ac:
        response = await ac.post(
            "/batch_insert/", files=files, params={"table": "INVALID"}
        )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_batch_insert_job(client: TestClient, mock_db_client):
    """Test batch inserting job data using a CSV file."""
    data = "1,Desarrollador\n" "2,Analista\n"
    files = {"file": ("test.csv", data, "text/csv")}
    mock_db_client.return_value = {"success": True, "rows_inserted": 2}

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as ac:
        response = await ac.post(
            "/batch_insert/", files=files, params={"table": TableName.JOB.value}
        )

    assert response.status_code == 200
    assert response.json() == {"success": True, "rows_inserted": 2}


@pytest.mark.asyncio
async def test_batch_insert_department(client: TestClient, mock_db_client):
    """Test batch inserting department data using a CSV file."""
    data = "1,Recursos Humanos\n" "2,Tecnología\n"
    files = {"file": ("test.csv", data, "text/csv")}
    mock_db_client.return_value = {"success": True, "rows_inserted": 2}

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as ac:
        response = await ac.post(
            "/batch_insert/", files=files, params={"table": TableName.DEPARTMENT.value}
        )

    assert response.status_code == 200
    assert response.json() == {"success": True, "rows_inserted": 2}
