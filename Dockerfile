# Dockerfile
FROM python:3.11
WORKDIR /src
COPY requirements.txt ./
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000

COPY wait-for-it.sh /wait-for-it.sh
RUN chmod +x /wait-for-it.sh

CMD ["./wait-for-it.sh", "db:5432", "--", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
