FROM python:3.12-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY pyproject.toml README.md /app/
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir .

COPY app /app/app
COPY bot /app/bot

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
