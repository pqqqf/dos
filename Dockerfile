FROM python:3.9-slim as builder

WORKDIR /app

# تثبيت الأدوات الأساسية
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# إنشاء بيئة افتراضية
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# تثبيت الحزم
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# --- مرحلة التشغيل النهائية ---
FROM python:3.9-slim

WORKDIR /app

# نسخ البيئة الافتراضية
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# نسخ الكود
COPY . .

CMD ["python", "bot.py"]
