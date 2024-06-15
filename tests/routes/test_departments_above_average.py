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
        "src.services.postgres_client.client.get_departments_above_average",
        new_callable=AsyncMock,
    )
    return mock


@pytest.mark.asyncio
async def test_departments_above_average(client: TestClient, mock_db_client):
    """Test retrieving departments whose performance is above average."""
    mock_db_client.return_value = [
        {"department": "Recursos Humanos", "performance": 85},
        {"department": "Tecnología", "performance": 90},
    ]

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as ac:
        response = await ac.get("/departments_above_average/")

    assert response.status_code == 200
    assert response.json() == [
        {"department": "Recursos Humanos", "performance": 85},
        {"department": "Tecnología", "performance": 90},
    ]
