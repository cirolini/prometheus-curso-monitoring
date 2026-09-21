FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .

EXPOSE 5000
# Uma worker so': o prometheus_client guarda estado em memoria, e com
# varias workers cada scrape cairia numa delas, dando numero errado.
# Para multi-worker existe o modo multiprocess da lib.
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "1", "app:app"]
