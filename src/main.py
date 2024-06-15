import logging
import uvicorn
from fastapi import FastAPI
from sqlalchemy import text
from src.routes.upload_csv import router as upload_csv_router
from src.routes.batch_insert import router as batch_insert_router
from src.routes.employees_per_quarter import router as employees_per_quarter_router
from src.routes.departments_above_average import router as departments_above_average_router
from src.services.postgres_client import client

app = FastAPI()

app.include_router(upload_csv_router)
app.include_router(batch_insert_router)
app.include_router(employees_per_quarter_router)
app.include_router(departments_above_average_router)

if __name__ == "__main__":
    client.init_db()
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)