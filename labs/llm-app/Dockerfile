FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY metrics.py provider.py agent.py app.py ./

EXPOSE 8000
# Uma worker so': o prometheus_client guarda estado em memoria.
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
