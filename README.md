
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
git clone https://github.com/yourusername/globant-challenge.git
cd globant-challenge
```

### Step 2: Create the `Dockerfile`

Ensure the `Dockerfile` is present in the root directory:

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY src/ .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Step 3: Create the `docker-compose.yml`

Ensure the `docker-compose.yml` file is present in the root directory:

```yaml
version: '3.8'

services:
  db:
    image: postgres:12
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
      POSTGRES_DB: dbname
    volumes:
      - postgres_data:/var/lib/postgresql/data

  api:
    build: .
    environment:
      DATABASE_URL: postgres://user:password@db/dbname
    ports:
      - "8000:8000"
    depends_on:
      - db

volumes:
  postgres_data:
```

### Step 4: Run the Containers

Build and run the containers using Docker Compose:

```bash
docker-compose up --build
```

The API should now be accessible at `http://localhost:8000`.

## Deployment on AWS EC2

### Step 1: Launch an EC2 Instance

- Launch an EC2 instance with Amazon Linux 2.
- Ensure the instance has a security group that allows inbound traffic on ports 22 (SSH) and 8000 (API).

### Step 2: Connect to Your EC2 Instance

Connect to your EC2 instance using SSH:

```bash
ssh -i /path/to/your-key.pem ec2-user@your-ec2-public-dns
```

### Step 3: Install Docker on the EC2 Instance

Install Docker and start the Docker service:

```bash
sudo yum update -y
sudo amazon-linux-extras install docker -y
sudo service docker start
sudo usermod -a -G docker ec2-user
```

Log out and log back in to apply the Docker group changes.

### Step 4: Copy Files to the EC2 Instance

Copy your project files to the EC2 instance. You can use `scp` to transfer files:

```bash
scp -i /path/to/your-key.pem -r /path/to/your-project ec2-user@your-ec2-public-dns:~
```

### Step 5: Build and Run the Containers on EC2

Connect to your EC2 instance, navigate to the project directory, and run the containers:

```bash
cd ~/your-project
docker-compose up --build -d
```

Your API should now be accessible at the public IP of your EC2 instance on port 8000.

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
