FROM python:3.12-slim
WORKDIR /app
COPY services/ai-ml-scoring/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY shared/ /app/shared/
COPY services/ai-ml-scoring/app/ /app/app/
COPY services/ai-ml-scoring/train_fraud_model.py /app/
EXPOSE 8009
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8009"]
