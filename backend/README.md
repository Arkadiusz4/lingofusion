# Lingofusion Backend

## Spis treści

- [Struktura projektu](#struktura-projektu)
- [Wymagania](#wymagania)
- [Budowanie obrazu Docker](#budowanie-obrazu-docker)
- [Uruchamianie serwera](#uruchamianie-serwera)
- [Endpoint `POST /api/predict`](#endpoint-post-apipredict)
- [Przykłady zapytań](#przykłady-zapytań)

---

## Struktura projektu

```markdown
backend/app
├── main.py
├── models/
│ ├── base.py
│ ├── translator.py
│ └── corrector.py
│
├── services/
│ ├── translation_service.py
│ └── correction_service.py
│
├── routes/
│ └── predict.py
│
├── schemas/
│ └── predict.py
│
├── utils/
│ └── highlight.py
│
└── init.py
```

- **`main.py`** – punkt wejścia aplikacji FastAPI, inicjalizuje modele przy starcie i rejestruje router.
- **`models/`** – ładowanie i przygotowanie modeli (PL→EN, EN→PL, korektor GEC w T5‐base).
- **`services/`** – asynchroniczne wywołania modeli w oddzielnym wątku (cache + ThreadPoolExecutor).
- **`routes/`** – definicja endpointu `POST /api/predict`.
- **`schemas/`** – Pydanticowe modele zapytań (`PredictRequest`) i odpowiedzi (`PredictResponse`, `Highlight`).
- **`utils/`** – funkcja `simple_highlight`, która na podstawie różnic między oryginałem a poprawką generuje listę
  fragmentów do podświetlenia.

---

## Wymagania

- Docker (zalecane) lub Python 3.10+ z zainstalowanymi pakietami:
    - `fastapi`
    - `uvicorn`
    - `torch>=2.0.0`
    - `transformers>=4.30.0`
    - `peft>=0.4.0`
    - `accelerate>=0.20.0`
    - `sentencepiece`
    - `onnxruntime`
    - `sacremoses`

Wersje pakietów znajdują się w `backend/requirements.txt`. Jeśli nie używasz Dockera, możesz odtworzyć środowisko
virtualenv i uruchomić:

```bash
python3 -m venv venv
source venv/bin/activate
pip install --no-cache-dir -r backend/requirements.txt
```

Następnie uruchamiamy aplikację lokalnie:

```bash
cd backend/app
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 1
```

---

## Budowanie obrazu Docker

W katalogu `backend/` znajduje się `Dockerfile`, który:

- Bazuje na `python:3.10-slim`.
- Instaluje zależności systemowe (m.in. `build-essential`, `gcc`, `libomp-dev`).
- Kopiuje `requirements.txt` i instaluje Pythonowe pakiety.
- Kopiuje źródła aplikacji do `/app/app`.
- Kopiuje lokalne foldery z adapterami LoRA do `/app/…`.
- Ustawia `CMD` na uruchomienie Uvicorna z 1 workerem (żeby nie powielać modeli w pamięci).

Aby zbudować obraz:

```bash
cd backend
docker build -t lingofusion-backend .
```

---

## Uruchamianie serwera

Po uruchomieniu zobaczysz w logach:

```less
[translator.py] Ładuję PL→EN tokenizer i bazowy model…
[translator.py] Ładuję PL→EN adapter LoRA z: /app/ helsinki_train20k_ep3_r8_len128/lora_adapter
[translator.py] Scalanie (merge) i kwantyzacja PL→EN…
[translator.py] ✔ PL→EN gotowe.
[translator.py] Ładuję EN→PL tokenizer i bazowy model…
[translator.py] Ładuję EN→PL adapter LoRA z: /app/ gsarti_enpl_train100k_ep7_r8_len128/lora_adapter
[translator.py] Scalanie (merge) i kwantyzacja EN→PL…
[translator.py] ✔ EN→PL gotowe.
```

Korektor GEC (T5-base) załaduje się dopiero przy pierwszym zapytaniu do `/api/predict?mode=correct`.

Po chwili (kilkanaście–kilkadziesiąt sekund na CPU) powinieneś zobaczyć:

```pgsql
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

Serwer jest teraz dostępny pod `http://localhost:8000`.

---

## Endpoint `POST /api/predict`

- URL: `/api/predict`
- Metoda: `POST`
- Nagłówek: `Content-Type: application/json`

### Request

```json
{
  "text": "<ciąg do przetworzenia>",
  "mode": "<tryb>"
}
```

- `text` – wielowierszowy string (może zawierać `\n`).
- `mode` – jeden z:
    - `translate-pl-en` – tłumaczenie z polskiego na angielski,
    - `translate-en-pl` – tłumaczenie z angielskiego na polski,
    - `correct` – korekta gramatyczna (GEC) w języku angielskim.

### Response (200 OK)

```json
{
  "output": "<wynikowy tekst (wielowierszowy)>",
  "highlights": [
    {
      "start": <int>,
      "end": <int>,
      "suggestion": "<tekst do podświetlenia>"
    },
    ...
  ]
}
```

- `output` – string z zachowanymi `\n` i przetworzonymi liniami.
- `highlights` – lista obiektów (tylko w trybie `correct`), gdzie każdy element `{ start, end, suggestion }` wskazuje
  fragment w `output` wymagający wyróżnienia. W trybach tłumaczenia `highlights` jest pustą listą.

---

## Przykłady zapytań

### 1. Tłumaczenie (PL→EN)

**Request**:

```http
POST /api/predict HTTP/1.1
Content-Type: application/json

{
  "text": "To jest test",
  "mode": "translate-pl-en"
}
```

**Response** (przykładowo):

```json
{
  "output": "This is a test",
  "highlights": []
}
```

### 2. Tłumaczenie (EN→PL)

**Request**:

```http
POST /api/predict HTTP/1.1
Content-Type: application/json

{
  "text": "How are you?",
  "mode": "translate-en-pl"
}
```

**Response** (przykładowo):

```json
{
  "output": "Witaj świecie\nJak się masz?",
  "highlights": []
}
```

### 3. Korekta (GEC)

**Request**:

```http
POST /api/predict HTTP/1.1
Content-Type: application/json

{
  "text": "I has a problm",
  "mode": "correct"
}
```

**Response** (przykładowo):

```json
{
  "output": "I have a problem\nShe don't like it",
  "highlights": [
    {
      "start": 2,
      "end": 6,
      "suggestion": "have"
    },
    {
      "start": 9,
      "end": 16,
      "suggestion": "problem"
    }
  ]
}
```

Fragmenty podane w `highlights` odpowiadają pozycjom w `output` (licząc od zera) – frontend może je podświetlić.

---

## Uwaga dot. zasobów i wydajności

- Cały proces ładowania trzech dużych modeli (Marian PL→EN, Marian EN→PL, T5‐base GEC) trwa na CPU kilkadziesiąt
  sekund–kilka minut przy pierwszym starcie. Następnie cache (`@lru_cache`) przyspiesza kolejne zapytania o identyczną
  linię.
- Korektor GEC ładuje się „leniwo” (dopiero przy pierwszym zapytaniu `mode="correct"`), co ogranicza czas startu w
  przypadku, gdy używasz tylko tłumaczenia.
- Kwantyzacja dynamiczna (`torch.quantization.quantize_dynamic`) znacząco zmniejsza pamięciożerność modeli i przyspiesza
  ich inferencję na CPU, kosztem minimalnej degradacji jakości.
