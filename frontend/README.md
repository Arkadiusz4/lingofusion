# LingoFusion Frontend

Poniższe README opisuje, jak zbudować i uruchomić frontend aplikacji Lingofusion — interfejs React/TypeScript oparty na
Vite, serwowany przez Nginx w kontenerze Dockerowym.

---

## Wymagania

- **Node.js 18+** (zalecane do lokalnego developmentu).
- **Docker** + **Docker Compose** (do produkcyjnego uruchomienia).

Aby uruchomić frontend lokalnie, wystarczy Node i npm/yarn. Aby zbudować i serwować w kontenerze, potrzebny jest Docker.

---

## Uruchomienie w trybie deweloperskim

1. Przejdź do katalogu `frontend/`:

```bash
cd frontend
```

2. Zainstaluj zależności (npm lub yarn):

```bash
npm install
# lub
yarn install
```

3. Uruchom serwer deweloperski Vite:

```bash
npm run dev
# lub
yarn dev
```

4. Otwórz w przeglądarce

```bash
http://localhost:5173
```

Domyślnie Vite działa na porcie `5173`. Aplikacja powinna odpalić się natychmiast i odświeżać na żywo (HMR).

### Konfiguracja adresu backendu

W pliku `src/api.ts` znajduje się URL do backendu:

```ts
export async function predict(req: PredictRequest): Promise<PredictResponse> {
    const {data} = await axios.post<PredictResponse>(
        'http://localhost:8000/api/predict',
        req
    );
    return data;
}
```

Jeśli backend jest dostępny pod innym adresem (np. przez proxy czy zdalny host), zmień URL w tym miejscu.

---

## Budowanie i uruchomienie w kontenerze

### Budowanie i start

1. Przejdź do katalogu `frontend/` i zbuduj obraz:

```bash
docker build -t lingofusion-frontend .
```

2. Uruchom kontener:

```bash
docker run -d -p 3000:80 lingofusion-frontend
```

3. Frontend będzie dostępny pod adresem:

```bash
http://localhost:3000
```

Nginx serwuje statyczne assety i przekierowuje wszystkie żądania (np. `/translate`) do `index.html` (React Router).

---

## Korzystanie z aplikacji

1. Otwórz `http://localhost:3000` w przeglądarce.
2. Przełączaj zakładki w nagłówku:
    - Tłumaczenie: wpisz tekst w polu „Wejście” (PL lub EN, w zależności od kierunku) i kliknij „Przetłumacz”.
    - Korekta: wpisz tekst w języku angielskim i kliknij „Sprawdź”.
3. Wynik pojawi się w panelu „Wyjście” lub „Poprawka”.
    - W przypadku korekty słowa z błędami są podświetlone i mają dymek (`title`) z zaleceniem.
    - W przypadku tłumaczenia otrzymasz pełen przetłumaczony tekst.
