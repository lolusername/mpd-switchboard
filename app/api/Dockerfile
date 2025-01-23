FROM python:3.12-slim

WORKDIR /app

# Install curl for healthcheck and build dependencies
RUN apt-get update && \
    apt-get install -y curl && \
    rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry

# Copy Poetry files
COPY pyproject.toml poetry.lock ./

# Install dependencies
RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi

# Copy the API code
COPY . .

# Add this line to make Python treat the directory as a package
ENV PYTHONPATH=/app

# For debugging
RUN ls -la /app

# Make sure we have all required files
RUN python -c "import auth; print('Auth module found')"

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]