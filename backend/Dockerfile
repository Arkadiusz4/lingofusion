FROM python:3.10-slim

WORKDIR /app

# 1) Zainstaluj sacremoses (tokenizator Marian)
RUN apt-get update && apt-get install -y build-essential gcc libomp-dev \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt .
# dopisz do requirements: sacremoses
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/app ./app
COPY notebooks/results_pl_en/helsinki_train20k_ep3_r8_len128/lora_adapter ./helsinki_train20k_ep3_r8_len128/lora_adapter
COPY notebooks/results_en_pl/gsarti_enpl_train100k_ep7_r8_len128/lora_adapter ./gsarti_enpl_train100k_ep7_r8_len128/lora_adapter
COPY notebooks/results_gec/t5-large_jfleg+nucle+bea_ep7_r8/lora_adapter ./t5-large_jfleg+nucle+bea_ep7_r8/lora_adapter

EXPOSE 8000

# 2) Ustaw 1 worker, żeby uniknąć forka przed załadowaniem modeli
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
