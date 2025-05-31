# =============================================================================
# Krok 1: Etap build z Node.js 18 (ponad Web Crypto API)
# =============================================================================
FROM node:18-slim AS builder

WORKDIR /app

# Skopiuj paczki i zainstaluj zależności
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

# Skopiuj cały kod frontendu i zbuduj
COPY frontend/ ./
RUN npm run build

# =============================================================================
# Krok 2: Etap produkcji z Nginx
# =============================================================================
FROM nginx:1.23-alpine

# Kopiujemy z poprzedniego etapu pliki statyczne do Nginx:
COPY --from=builder /app/dist /usr/share/nginx/html

# Podmieniamy domyślną konfigurację Nginx na proxy + statyczne
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
