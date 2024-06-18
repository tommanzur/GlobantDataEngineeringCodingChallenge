
# Globant Data Engineering Coding Challenge

## Description

This project is part of Globant's Data Engineering coding challenge. The solution includes creating a REST API to handle historical employee data and perform specific queries on this data.

## Requirements

- Docker
- Docker Compose

## Running Locally

### Step 1: Clone the Repository

Clone the repository to your local machine:

```bash
git clone https://github.com/tommanzur/GlobantDataEngineeringCodingChallenge.git
cd GlobantDataEngineeringCodingChallenge
```

### Step 2: Run Docker Compose

Run the containers using Docker Compose:

```bash
docker-compose up --build
```

The API should now be accessible at `http://localhost:8000`.

### Accessing the UI

- Swagger UI: `http://localhost:8000/docs`
- pgAdmin: `http://localhost:80`

## Deployment on AWS EC2 via GitHub Actions

### Step 1: Launch an EC2 Instance

Launch an EC2 instance with Ubuntu. Ensure the instance has a security group that allows inbound traffic on ports 22 (SSH), 8000 (API), and 80 (pgAdmin).

### Step 2: Configure GitHub Secrets

To deploy using GitHub Actions, configure the following secrets in your GitHub repository:

- DOCKER_PASSWORD
- DOCKER_USERNAME
- EC2_SSH_KEY
- HOST_DNS
- PGADMIN_DEFAULT_EMAIL
- PGADMIN_DEFAULT_PASSWORD
- POSTGRES_DB
- POSTGRES_PASSWORD
- POSTGRES_USER
- TARGET_DIR
- USERNAME

### Step 3: Push Changes to GitHub

Push your changes to the repository to trigger the GitHub Actions workflow. The workflow will build and deploy the application to your EC2 instance.

### Step 4: Access the Application

Once deployed, you can access the API at the public IP of your EC2 instance on port 8000.

## Endpoints

- `/upload_csv/` : Upload CSV files.
- `/batch_insert/` : Insert batch transactions.
- `/employees_per_quarter/` : Get the number of employees hired per quarter in 2021.
- `/departments_above_average/` : Get departments that hired more than the average in 2021.

## Testing

To run unit tests:

```bash
pytest
```

The API and the database are containerized, and you only need to start Docker Compose.
