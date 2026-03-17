FROM python:3.12-slim
WORKDIR /app
COPY services/sanctions-screening/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY shared/ /app/shared/
COPY services/sanctions-screening/app/ /app/app/
EXPOSE 8003
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8003"]
