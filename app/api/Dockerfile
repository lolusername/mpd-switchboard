FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY pyproject.toml poetry.lock ./
RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --only main

# Copy the API code
COPY . .

# For debugging
RUN ls -la /app

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]