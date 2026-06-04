# ─── Stage 1: Builder ───────────────────────────────────────────────────────
# Sử dụng image gọn nhẹ với Python 3.13 slim để build dependencies
FROM python:3.13-slim AS builder

# Thiết lập thư mục làm việc
WORKDIR /app

# Cài đặt các công cụ build cần thiết (cho bcrypt, motor, v.v.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy file requirements trước để tận dụng Docker layer cache
COPY requirements/ requirements/

# Cài đặt dependencies vào thư mục /install để copy sang stage tiếp theo
RUN pip install --upgrade pip && \
    pip install --prefix=/install --no-cache-dir -r requirements/base.txt


# ─── Stage 2: Runner ───────────────────────────────────────────────────────
# Image cuối cùng gọn nhẹ, không chứa các công cụ build
FROM python:3.13-slim AS runner

# Thiết lập biến môi trường Python để không tạo .pyc files
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app

# Copy Python packages đã được build từ builder stage
COPY --from=builder /install /usr/local

# Copy toàn bộ source code
COPY src/ src/
COPY static/ static/
COPY templates/ templates/
COPY logging.ini logging.ini

# Tạo thư mục để mount GCS credentials file từ host
RUN mkdir -p /app/credentials

# Expose port - Cloud Run sẽ inject biến PORT (thường 8080), local mặc định 8000
EXPOSE 8080

# Dùng shell form để đọc biến $PORT từ môi trường (Cloud Run yêu cầu)
CMD uvicorn src.main:app --host 0.0.0.0 --port ${PORT:-8000}
