FROM python:3.11.9-slim

EXPOSE 8000

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

COPY ./requirements.txt .

RUN pip install --no-cache-dir \
    torch==2.14.0 \
    torchvision==0.29.0 \
    --index-url https://download.pytorch.org/whl/cpu

RUN pip install --no-cache-dir -r requirements.txt

COPY alembic.ini .
COPY migrations ./migrations

COPY src ./src

CMD ["python", "-m", "src.main"]