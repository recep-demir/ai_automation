# --- Aşama 1: Builder (Derleme) ---
FROM python:3.12-alpine AS builder

WORKDIR /app

# Derleme araçlarını kur (gcc, musl vb. pydantic_core gibi paketler için gerekebilir)
RUN apk add --no-cache gcc musl-dev python3-dev libffi-dev

COPY requirements.txt .

# Paketleri bir klasöre kuruyoruz
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# --- Aşama 2: Runtime (Çalışma) ---
FROM python:3.12-alpine

WORKDIR /app

# Sadece kurulmuş paketleri builder'dan kopyala
COPY --from=builder /install /usr/local
COPY . .

# Python ayarları
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

EXPOSE 8000

# Uygulamayı başlat
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]