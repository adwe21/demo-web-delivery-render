FROM node:18-alpine AS frontend-builder
WORKDIR /app/web
COPY web/package*.json ./
RUN npm install
COPY web/ ./
RUN npm run build

FROM python:3.13-slim AS runtime
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY web/backend ./web/backend
COPY web/backend/data ./web/backend/data
COPY --from=frontend-builder /app/web/dist ./web/dist
EXPOSE 8080
CMD ["python", "-m", "uvicorn", "web.backend.deploy_app:app", "--host", "0.0.0.0", "--port", "8080"]
