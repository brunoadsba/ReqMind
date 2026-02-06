FROM python:3.12-slim

# Instala dependências de sistema necessárias (mídia + magic)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      ffmpeg \
      tesseract-ocr \
      tesseract-ocr-por \
      libmagic1 && \
    rm -rf /var/lib/apt/lists/*

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    CHARSET_NORMALIZER_PURE_PYTHON=1 \
    TZ=America/Sao_Paulo

WORKDIR /app

# Dependências Python
COPY requirements.txt pyproject.toml ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Código-fonte
COPY . .

ENV PYTHONPATH=/app/src

# O .env deve ser montado em /app/.env via --env-file
CMD ["python", "src/bot_simple.py"]

