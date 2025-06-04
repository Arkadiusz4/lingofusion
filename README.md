# LingoFusion

LingoFusion to kompletny zestaw narzędzi do tłumaczeń PL↔EN oraz korekty angielskich tekstów (GEC), składający się z:

- **Backendu** (FastAPI + Python + PEFT/LoRA + dynamiczna kwantyzacja na CPU)
- **Frontendu** (React + TypeScript + Vite, serwowany przez Nginx w kontenerze Docker)
- **Notebooków** z wynikami treningu adapterów LoRA oraz skryptami do ich generowania
- **Zestawu danych** do trenowania adapterów (20 000 par zdań PL↔EN) oraz korpusów GEC

Poniżej znajdziesz opis struktury projektu, użytych technologii, instrukcję uruchomienia i informacje o notebookach oraz
danych.

---

## Spis treści

1. [Czym jest LingoFusion?](#czym-jest-lingofusion)
2. [Technologie](#technologie)
3. [Jak uruchomić całość (Docker Compose)](#jak-uruchomić-całość-docker-compose)
4. [Szybki start – backend](#szybki-start--backend)
5. [Szybki start – frontend](#szybki-start--frontend)
6. [Opis notebooków](#opis-notebooków)
7. [Zestaw danych](#zestaw-danych)

---

## Czym jest LingoFusion?

LingoFusion to prototypowa aplikacja pełnego cyklu:

1. **Tłumaczenie** tekstu — obsługa wielu zdań i zachowanie struktury wielowierszowej.
2. **Korekta** gramatyczna (GEC) — podkreślanie wprowadzonych zmian w tekście angielskim.

Backend wykorzystuje modele Marian (Helsinki-NLP/opus-mt-pl-en i gsarti/opus-mt-tc-en-pl) z adapterami LoRA, a także
model T5-base „vennify/t5-base-grammar-correction” do korekty. Modele są scalane („merge-and-unload”) i dynamicznie
kwantyzowane do INT8, by działały akceptowalnie na CPU. Frontend to prosta aplikacja React/TypeScript, której zadaniem
jest wygodne wprowadzanie tekstu, wybór trybu i wyświetlanie wyników wraz z podświetleniami.

---

## Technologie

- **Python 3.10 + FastAPI** – backend API.
- **Torch 2.x + Transformers 4.x + PEFT 0.4** – ładowanie bazowych modeli, adapterów LoRA i dynamiczna kwantyzacja.
- **Hugging Face Pipeline** – prosty interfejs do generacji (korektor).
- **Pydantic** – walidacja request/response JSON.
- **React 18 + TypeScript + Vite** – frontendowa aplikacja z kilkoma komponentami (textarea, przyciski, highlight).
- **Axios** – do wywoływania endpointów backendu.
- **Docker + Docker Compose** – konteneryzacja backendu i frontendu (Nginx do serwowania buildu Reacta).
- **Nginx** – prosty serwer statyczny dla frontendowego buildu.
- **Difflib (własny highlight)** – algorytm SequenceMatcher do porównania oryginału i korekty.
- **Jupyter Notebook** – notebooki do treningu adapterów LoRA (Marian + T5) i zapisywania wyników.

---

## Jak uruchomić całość (Docker Compose)

1. **Zainstaluj** Docker i Docker Compose (wersja `1.29.0+` lub `v2`).
2. Upewnij się, że w projekcie znajdują się foldery `helsinki_train20k_ep3_r8_len128`,
   `gsarti_enpl_train100k_ep7_r8_len128` (z podfolderem `lora_adapter`), oraz
   `t5-large_jfleg+nucle+bea_ep7_r8/lora_adapter`.
3. W głównym katalogu (tam, gdzie jest `docker-compose.yml`) uruchom:

```bash
docker compose up --build
```

Docker Compose:

- Buduje obraz backend z `backend/Dockerfile`,
- Buduje obraz frontend z `frontend/Dockerfile`,

Tworzy dwa kontenery:

- `lingofusion-backend` (podłączony do portu `8000`),
- `lingofusion-frontend` (podłączony do portu `3000`),

4. Po kilku-kilkunastu minutach (ze względu na wstępne ładowanie i kwantyzację modeli, zwłaszcza GEC) zobaczysz w
   logach:

- Backend (FastAPI) gotowy do przyjmowania requestów:

```less
[translator.py] ✔ PL→EN gotowe.
[translator.py] ✔ EN→PL gotowe.
INFO: Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

- Frontend (Nginx) gotowy:

```less
2025/06/XX XX:XX:XX [notice] nginx/1.23.4/2025/06/
XX XX:XX:XX [notice] start worker process 1
```

5. Otwórz przeglądarkę:

- Frontend: `http://localhost:3000`
- Backend (na potrzeby testów, np. `curl`): `http://localhost:8000/api/predict`

--- 

## Szybki start – backend

Jeśli chcesz uruchomić tylko backend lokalnie (bez Dockera):

1. Skonfiguruj wirtualne środowisko:

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install --no-cache-dir -r requirements.txt
```

2. Uruchom serwer:

```bash
cd app
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 1
```

Przy starcie zobaczysz w logach:

```less
[translator.py] Ładuję PL→EN tokenizer i bazowy model…
[translator.py] Ładuję PL→EN adapter LoRA z: /ścieżka/do/helsinki_train.../lora_adapter
[translator.py] Scalanie PL→EN… ✔
[translator.py] Ładuję EN→PL tokenizer i bazowy model…
[translator.py] Ładuję EN→PL adapter LoRA… ✔
INFO: 127.0.0.1:XXXX - "GET /docs HTTP/1.1" 200 OK
...
```

3. Sprawdź w przeglądarce dokumentację Swagger UI:

```bash
http://localhost:8000/docs
```

Wywołuj endpoint `POST /api/predict` zgodnie z opisem w README backendu.

---

## Szybki start – frontend

Jeśli chcesz uruchomić frontend samodzielnie (development):

1. Przejdź do katalogu frontend/ i zainstaluj zależności:

```bash
cd frontend
npm install
```

2. Upewnij się, że backend jest uruchomiony pod adresem `http://localhost:8000`.

3. Uruchom Vite:

```bash
npm run dev
```

4. Otwórz przeglądarkę:

```bash
http://localhost:5173
```

Frontend powinien natychmiast się uruchomić, a zmiany w kodzie będą odświeżane na żywo.

---

## Opis notebooków

W katalogu `notebooks/` znajdują się Jupyter Notebooki użyte do trenowania adapterów LoRA i ewaluacji modeli:

- `train_pl_en.ipynb`
    - Wczytanie datasetu PL↔EN (20 000 par zdań).
    - Przygotowanie pipeline do generacji (`Helsinki-NLP/opus-mt-pl-en`).
    - Instalacja i konfiguracja PEFT LoRA (parametry: epoki, r, α).
    - Trenowanie adaptera LoRA przez kilka epok.
    - Zapis adapterów do folderu `notebooks/results_pl_en/helsinki_train20k_ep3_r8_len128/lora_adapter`.

- `train_en_pl.ipynb`

  Analogicznie:
    - Wczytanie tego samego datasetu w odwróconej kolejności (zdanie EN + odpowiadające PL).
    - Trenowanie adaptera LoRA w modelu gsarti/opus-mt-tc-en-pl.
    - Zapis wyników do `notebooks/results_en_pl/gsarti_enpl_train100k_ep7_r8_len128/lora_adapter`.

- `train_gec.ipynb`
    - Wczytanie korpusów gramatycznych (JFLEG, NuCLE, BEA).
    - Przygotowanie modelu T5-large i adaptera LoRA (parametry treningu).
    - Trenowanie adaptera GEC.
    - Zapis adaptera do `notebooks/results_gec/t5-large_jfleg+nucle+bea_ep7_r8/lora_adapter`.

  _W praktyce w finalnym rozwiązaniu używamy publicznego modelu GEC na T5-base, dlatego lokalny adapter T5-large nie
  jest
  ładowany._

- `data/`
  Skrypty i pliki pomocnicze do ekstrakcji i wstępnego przetwarzania danych:
    - `pl_en_20k.csv` z parowanymi zdaniami PL↔EN.
    - Skrypty do czyszczenia i tokenizacji (np. usuwanie HTML, normalizacja).

- `results_pl_en/`, `results_en_pl/`, `results_gec/`

  Foldery z wytrenowanymi adapterami LoRA, które kopiujemy później do obrazu Dockerowego backendu. Każdy katalog
  `…/lora_adapter` zawiera pliki:
    - `adapter_config.json`
    - `pytorch_model.bin`
    - inne pliki niezbędne do odtworzenia adaptera LoRA bez łączenia z HF.

--- 

## Zestaw danych

- PL↔EN (20 000 par)
    - Źródło: różne opensource’owe parallel corpora (np. OPUS, OpenSubtitles, itp.), przefiltrowane i wyekstrahowane 20
      000
      jakościowych par zdań.
    - Format: CSV z kolumnami `pl_text`, `en_text`.
    - Służy jako trening i walidacja adapterów LoRA dla Marian.

- GEC (Grammar Error Correction)
    - Korzystamy z kombinacji trzech korpusów:
        - JFLEG (https://github.com/keisks/jfleg)
        - NuCLE (http://www.comp.nus.edu.sg/~nlp/syntax/nucle.html)
        - BEA 2019 (http://www.bea-university.org/2019)
    - Notebook `train_gec.ipynb` łączy te zasoby, przygotowuje wejście „gec: <tekst>” oraz wyjście (poprawione zdanie).
    - Adapter LoRA dla T5-large jest trenowany na tym połączeniu, lecz w finalnym API korzystamy z publicznego
      `vennify/t5-base-grammar-correction`.

