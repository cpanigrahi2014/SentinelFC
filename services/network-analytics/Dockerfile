FROM python:3.12-slim
WORKDIR /app
COPY services/network-analytics/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY shared/ /app/shared/
COPY services/network-analytics/app/ /app/app/
EXPOSE 8007
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8007"]
