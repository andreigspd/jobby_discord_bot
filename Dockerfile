# Jobby Discord Bot — container image
FROM python:3.12-slim

# Don't buffer stdout/stderr so logs show up in `docker logs` in real time.
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Install dependencies first for better layer caching.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code.
COPY . .

# Store the SQLite database on a mounted volume so state survives restarts.
# database.py reads this env var (see JOBS_DB_PATH handling).
ENV JOBS_DB_PATH=/data/jobs.db
VOLUME ["/data"]

# Run as a non-root user for safety.
RUN useradd --create-home --uid 1000 appuser \
    && mkdir -p /data \
    && chown -R appuser:appuser /app /data
USER appuser

CMD ["python", "main.py"]
