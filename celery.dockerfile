FROM python:3.8-slim

WORKDIR /app

# Install Poetry
RUN pip install poetry

# Copy poetry files
COPY pyproject.toml poetry.lock ./

# Install dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev --no-interaction --no-ansi

# Copy application code
COPY . .

# Run Celery worker
CMD ["poetry", "run", "celery", "-A", "app.worker.celery_app", "worker", "--loglevel=info"]
