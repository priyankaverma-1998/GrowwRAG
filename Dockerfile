FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN python -m src.ingestion.run_pipeline
EXPOSE 5000
CMD ["python", "-m", "src.app"]
