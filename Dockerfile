FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y curl && \
    rm -rf /var/lib/apt/lists/*

RUN pip install poetry

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi && \
    pip install elasticsearch==7.10.1 boto3

COPY . .

ENV PYTHONPATH=/app

RUN ls -la /app

RUN python -c "import auth; print('Auth module found')"

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"] 