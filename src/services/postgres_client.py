from io import StringIO
import logging
import os
from fastapi.responses import JSONResponse
import numpy as np
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import scoped_session, sessionmaker
from src.models import db
from src.models.department import Department
from src.models.employee import Employee
from src.models.job import Job

class PostgresClient:
    """
    PostgresClient handles database connections and operations for the application.
    """

    def __init__(self):
        """Initialize the database client with connection settings."""
        self.database_url = (
            f"postgresql+psycopg2://{os.getenv('POSTGRES_USER', 'user')}:"
            f"{os.getenv('POSTGRES_PASSWORD', 'admin')}@"
            f"{os.getenv('POSTGRES_HOST', 'db')}/"
            f"{os.getenv('POSTGRES_DB', 'globant_challenge')}"
        )
        logging.info(f"Connecting to database at {self.database_url}")
        self.engine = create_engine(self.database_url)
        self.session_factory = sessionmaker(bind=self.engine)
        self.Session = scoped_session(self.session_factory)

    def init_db(self):
        """Initialize the database by creating all defined tables."""
        db.metadata.create_all(self.engine)
        logging.info("Database initialized")

    async def handle_upload(self, file, table):
        """
        Handle the upload and insertion of CSV data into the specified table.

        Args:
            file: The uploaded file containing CSV data.
            table: The name of the table to insert data into.
        """
        session = self.Session()
        try:
            contents = await file.read()
            if table == 'employee':
                column_names = ['id', 'name', 'datetime', 'department_id', 'job_id']
            elif table == 'job':
                column_names = ['id', 'job']
            elif table == 'department':
                column_names = ['id', 'department']
            else:
                raise ValueError("Invalid table name")

            df = pd.read_csv(StringIO(contents.decode("utf-8")), header=None, names=column_names)
            logging.info(
                f"DataFrame loaded with shape {df.shape} and columns {df.columns.tolist()}"
                )

            if table == 'department':
                self._insert_departments(df, session)
            elif table == 'job':
                self._insert_jobs(df, session)
            elif table == 'employee':
                self._insert_employees(df, session)

            session.commit()
            logging.info("Data committed to the database")

        except (SQLAlchemyError, Exception) as e:
            session.rollback()
            logging.error(f"Error during data insertion: {e}")
            raise e

        finally:
            session.close()
        return {"filename": file.filename}

    async def handle_batch_insert(self, rows, table):
        """
        Handle batch insertion of data into the specified table.

        Args:
            rows: List of dictionaries representing rows to insert.
            table: The name of the table to insert data into.
        """
        session = self.Session()
        try:
            df = pd.DataFrame(rows)
            logging.info(
                f"Batch DataFrame loaded with shape {df.shape} and columns {df.columns.tolist()}"
                )

            if table == 'department':
                data_to_insert = df.to_dict(orient='records')
                session.bulk_insert_mappings(Department, data_to_insert)
            elif table == 'job':
                data_to_insert = df.to_dict(orient='records')
                session.bulk_insert_mappings(Job, data_to_insert)
            elif table == 'employee':
                df = self._prepare_employee_dataframe(df)
                data_to_insert = df.to_dict(orient='records')
                session.bulk_insert_mappings(Employee, data_to_insert)

            session.commit()
            logging.info("Batch data committed to the database")

        except (SQLAlchemyError, Exception) as e:
            session.rollback()
            logging.error(f"Error during batch insertion: {e}")
            raise e

        finally:
            session.close()
        return {"status": "success", "rows_inserted": len(rows)}

    async def get_employees_per_quarter(self):
        """
        Get the number of employees hired per quarter for each department and job.
        """
        session = self.Session()
        try:
            query = text("""
                SELECT 
                    d.department AS department, 
                    j.job AS job,
                    SUM(CASE WHEN EXTRACT(QUARTER FROM e.datetime) = 1 THEN 1 ELSE 0 END) AS Q1,
                    SUM(CASE WHEN EXTRACT(QUARTER FROM e.datetime) = 2 THEN 1 ELSE 0 END) AS Q2,
                    SUM(CASE WHEN EXTRACT(QUARTER FROM e.datetime) = 3 THEN 1 ELSE 0 END) AS Q3,
                    SUM(CASE WHEN EXTRACT(QUARTER FROM e.datetime) = 4 THEN 1 ELSE 0 END) AS Q4
                FROM 
                    employees e
                JOIN 
                    departments d ON e.department_id = d.id
                JOIN 
                    jobs j ON e.job_id = j.id
                WHERE 
                    EXTRACT(YEAR FROM e.datetime) = 2021
                GROUP BY 
                    d.department, j.job
                ORDER BY 
                    d.department, j.job
            """)

            result = session.execute(query).fetchall()
            df = pd.DataFrame(result, columns=['department', 'job', 'Q1', 'Q2', 'Q3', 'Q4'])
            data = df.to_dict(orient='records')

            return JSONResponse(content={"data": data})

        except SQLAlchemyError as e:
            session.rollback()
            logging.error(f"SQLAlchemyError: {e}")
            raise e

        finally:
            session.close()

    async def get_departments_above_average(self):
        """
        Get departments that hired more employees than the average number of hires in 2021.
        """
        session = self.Session()
        try:
            subquery = text("""
                SELECT 
                    department_id, COUNT(id) AS hired_count
                FROM 
                    employees
                WHERE 
                    EXTRACT(YEAR FROM datetime) = 2021
                GROUP BY 
                    department_id
            """)

            avg_hired_query = text(f"""
                SELECT 
                    AVG(hired_count) 
                FROM 
                    ({subquery}) AS sub
            """)

            avg_hired = session.execute(avg_hired_query).scalar()

            query = text("""
                SELECT 
                    d.id, d.department, COUNT(e.id) AS hired
                FROM 
                    employees e
                JOIN 
                    departments d ON e.department_id = d.id
                WHERE 
                    EXTRACT(YEAR FROM e.datetime) = 2021
                GROUP BY 
                    d.id, d.department
                HAVING 
                    COUNT(e.id) > :avg_hired
                ORDER BY 
                    COUNT(e.id) DESC
            """)

            result = session.execute(query, {"avg_hired": avg_hired}).fetchall()
            df = pd.DataFrame(result, columns=['id', 'department', 'hired'])
            logging.info(f"Departments above average: {df.to_dict(orient='records')}")

            data = df.to_dict(orient='records')
            return JSONResponse(content={"data": data})

        except SQLAlchemyError as e:
            session.rollback()
            logging.error(f"SQLAlchemyError: {e}")
            raise e

        finally:
            session.close()

    def _insert_departments(self, df, session):
        """Helper method to insert departments data."""
        for _, row in df.iterrows():
            session.add(Department(id=row['id'], department=row['department']))

    def _insert_jobs(self, df, session):
        """Helper method to insert jobs data."""
        for _, row in df.iterrows():
            session.add(Job(id=row['id'], job=row['job']))

    def _insert_employees(self, df, session):
        """Helper method to insert employees data."""
        try:
            df['datetime'] = pd.to_datetime(df['datetime'], utc=True, errors='coerce')
        except Exception as e:
            logging.error(f"Initial date parsing failed: {e}")

        df = df.replace({pd.NaT: None, np.NaN: None})
        for _, row in df.iterrows():
            session.add(Employee(
                id=row['id'],
                name=row['name'],
                datetime=row['datetime'],
                department_id=row['department_id'],
                job_id=row['job_id']
            ))

    def _prepare_employee_dataframe(self, df):
        """Helper method to prepare the employee DataFrame."""
        try:
            df['datetime'] = pd.to_datetime(df['datetime'], utc=True, errors='coerce')
        except Exception as e:
            logging.error(f"Initial date parsing failed: {e}")

        df = df.replace({pd.NaT: None, np.NaN: None})
        return df

client = PostgresClient()
