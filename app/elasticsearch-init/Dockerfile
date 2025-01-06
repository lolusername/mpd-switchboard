FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY pyproject.toml poetry.lock ./
RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --only main

# Copy the entire elasticsearch-init directory
COPY elasticsearch-init/ /app/elasticsearch-init/

# For debugging
RUN ls -la /app/elasticsearch-init/

CMD ["python", "elasticsearch-init/main.py"]