import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport
from src.main import app
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
        "src.services.postgres_client.client.get_employees_per_quarter",
        new_callable=AsyncMock,
    )
    return mock


@pytest.mark.asyncio
async def test_employees_per_quarter(client: TestClient, mock_db_client):
    """Test retrieving the number of employees per quarter."""
    mock_db_client.return_value = [
        {"quarter": "Q1", "employees": 120},
        {"quarter": "Q2", "employees": 150},
        {"quarter": "Q3", "employees": 100},
        {"quarter": "Q4", "employees": 130},
    ]

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as ac:
        response = await ac.get("/employees_per_quarter/")

    assert response.status_code == 200
    assert response.json() == [
        {"quarter": "Q1", "employees": 120},
        {"quarter": "Q2", "employees": 150},
        {"quarter": "Q3", "employees": 100},
        {"quarter": "Q4", "employees": 130},
    ]
