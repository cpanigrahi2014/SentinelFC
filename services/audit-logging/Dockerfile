FROM python:3.12-slim
WORKDIR /app
COPY services/audit-logging/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY shared/ /app/shared/
COPY services/audit-logging/app/ /app/app/
EXPOSE 8011
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8011"]
