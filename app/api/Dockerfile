FROM python:3.12-slim

WORKDIR /app

# Install curl for healthcheck
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Copy only the requirements files first
COPY pyproject.toml poetry.lock ./

# Install dependencies
RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --only main

# Copy the API code
COPY . .

# For debugging
RUN ls -la /app

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]