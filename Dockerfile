# Vega — containerized run. Reproducible engine + inference + dbt(duckdb) pipeline.
FROM python:3.11-slim

WORKDIR /app

# Install deps first for layer caching.
COPY pyproject.toml README.md ./
RUN pip install --no-cache-dir ".[dbt]" || true

# Copy the project.
COPY . .
RUN pip install --no-cache-dir -e ".[dbt]"

# Default: run the full pipeline (engine -> metrics -> infer) from config.yaml.
ENTRYPOINT ["python", "-m", "cli"]
CMD ["all"]
