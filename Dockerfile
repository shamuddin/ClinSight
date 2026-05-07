# ClinSight Full Stack Dockerfile
# Stage 1: Python backend with AMD ROCm support
FROM rocm/dev-ubuntu-22.04:latest AS backend

WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 python3-pip curl git \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt* /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt || true

COPY backend/ /app/backend/
COPY scripts/ /app/scripts/
COPY tests/ /app/tests/
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Stage 2: Frontend build
FROM node:20-alpine AS frontend-build
WORKDIR /app
COPY frontend/react-app/package*.json ./
RUN npm ci
COPY frontend/react-app/ ./
RUN npm run build

# Stage 3: Production — nginx + backend
FROM nginx:alpine AS production
RUN apk add --no-cache python3 py3-pip curl

# Install backend deps
COPY requirements.txt /tmp/requirements.txt
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt || true

# Copy backend
COPY backend/ /app/backend/
COPY scripts/ /app/scripts/
COPY tests/ /app/tests/
COPY frontend/react-app/dist/ /usr/share/nginx/html/

# Nginx config
COPY docker/nginx.conf /etc/nginx/conf.d/default.conf

# Start script
COPY docker/start.sh /start.sh
RUN chmod +x /start.sh

EXPOSE 80 8002
CMD ["/start.sh"]
