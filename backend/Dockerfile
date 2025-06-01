FROM python:3.10-slim

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/app ./app

COPY notebooks/results_pl_en/helsinki_train20k_ep3_r8_len128/lora_adapter ./helsinki_train20k_ep3_r8_len128/lora_adapter

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
