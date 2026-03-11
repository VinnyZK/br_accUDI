# ── API ──────────────────────────────────────────
FROM python:3.12-slim AS api

WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*
COPY api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY api/src/ ./src/
ENV PYTHONPATH=/app/src

CMD ["uvicorn", "openudi.main:app", "--host", "0.0.0.0", "--port", "8000"]

# ── Frontend build ───────────────────────────────
FROM node:22-slim AS frontend-build

WORKDIR /app
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install
COPY frontend/ .
RUN npm run build

# ── Frontend serve ───────────────────────────────
FROM nginx:alpine AS frontend

COPY --from=frontend-build /app/dist /usr/share/nginx/html
COPY infra/nginx/default.conf /etc/nginx/conf.d/default.conf
EXPOSE 3000
CMD ["nginx", "-g", "daemon off;"]

# ── ETL ──────────────────────────────────────────
FROM python:3.12-slim AS etl

WORKDIR /workspace
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
COPY etl/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
