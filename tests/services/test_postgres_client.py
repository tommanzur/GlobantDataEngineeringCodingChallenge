import pytest
import pandas as pd
from unittest.mock import patch, MagicMock, AsyncMock
from src.services.postgres_client import PostgresClient


@pytest.fixture
def postgres_client():
    """Fixture to provide a mocked PostgresClient."""
    with patch("src.services.postgres_client.create_engine") as mock_create_engine:
        mock_engine = MagicMock()
        mock_create_engine.return_value = mock_engine
        client = PostgresClient()
        yield client


@pytest.fixture
def mock_session():
    """Fixture to provide a mocked database session."""
    with patch("src.services.postgres_client.scoped_session") as mock_scoped_session:
        mock_session_factory = MagicMock()
        mock_scoped_session.return_value = mock_session_factory
        mock_session = MagicMock()
        mock_session_factory.return_value = mock_session
        yield mock_session


def test_init_db(postgres_client):
    """Test the initialization of the database."""
    with patch(
        "src.services.postgres_client.db.metadata.create_all"
    ) as mock_create_all:
        postgres_client.init_db()
        mock_create_all.assert_called_once_with(postgres_client.engine)


@pytest.mark.asyncio
async def test_handle_upload_employee(postgres_client):
    """Test handling the upload of employee data."""
    file_content = "1,Diego,2021-01-01 00:00:00,1,1\n2,Ana,2021-02-01 00:00:00,1,2"
    file = MagicMock()
    file.read = AsyncMock(return_value=file_content.encode("utf-8"))
    table = "employee"

    with patch.object(postgres_client, "_insert_employees") as mock_insert:
        response = await postgres_client.handle_upload(file, table)
        mock_insert.assert_called_once()
        assert response == {"filename": file.filename}


@pytest.mark.asyncio
async def test_handle_upload_invalid_table(postgres_client):
    """Test handling upload with an invalid table name."""
    file_content = "1,Diego,2021-01-01 00:00:00,1,1"
    file = MagicMock()
    file.read = AsyncMock(return_value=file_content.encode("utf-8"))
    table = "invalid_table"

    with pytest.raises(ValueError):
        await postgres_client.handle_upload(file, table)


@pytest.mark.asyncio
async def test_handle_batch_insert_employee(postgres_client, mock_session):
    """Test batch inserting employee data."""
    rows = [
        {
            "id": 1,
            "name": "Diego",
            "datetime": "2021-01-01 00:00:00",
            "department_id": 1,
            "job_id": 1,
        },
        {
            "id": 2,
            "name": "Ana",
            "datetime": "2021-02-01 00:00:00",
            "department_id": 1,
            "job_id": 2,
        },
    ]
    table = "employee"

    with patch.object(
        postgres_client, "_prepare_employee_dataframe", return_value=pd.DataFrame(rows)
    ) as mock_prepare:
        with patch.object(mock_session, "bulk_insert_mappings") as mock_bulk_insert:
            response = await postgres_client.handle_batch_insert(rows, table)
            mock_prepare.assert_called_once()
            mock_bulk_insert.assert_called_once()
            assert response == {"status": "success", "rows_inserted": len(rows)}


@pytest.mark.asyncio
async def test_get_employees_per_quarter(postgres_client, mock_session):
    """Test retrieving employee count per quarter."""
    result_data = [("Finance", "Analyst", 1, 2, 0, 0), ("IT", "Developer", 0, 1, 3, 1)]
    expected_data = [
        {"department": "Finance", "job": "Analyst", "Q1": 1, "Q2": 2, "Q3": 0, "Q4": 0},
        {"department": "IT", "job": "Developer", "Q1": 0, "Q2": 1, "Q3": 3, "Q4": 1},
    ]

    mock_session.execute.return_value.fetchall.return_value = result_data

    response = await postgres_client.get_employees_per_quarter()
    assert response.status_code == 200
    assert response.json() == {"data": expected_data}


@pytest.mark.asyncio
async def test_get_departments_above_average(postgres_client, mock_session):
    """Test retrieving departments with above average hires."""
    avg_hired_data = 5
    result_data = [(1, "Finance", 10), (2, "IT", 7)]
    expected_data = [
        {"id": 1, "department": "Finance", "hired": 10},
        {"id": 2, "department": "IT", "hired": 7},
    ]

    mock_session.execute.side_effect = [MagicMock(scalar=avg_hired_data), result_data]

    response = await postgres_client.get_departments_above_average()
    assert response.status_code == 200
    assert response.json() == {"data": expected_data}
