FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --only main && \
    pip install elasticsearch==7.10.1 boto3 pdfminer.six tqdm

COPY elasticsearch-init/ /app/elasticsearch-init/

RUN ls -la /app/elasticsearch-init/

CMD ["python", "elasticsearch-init/main.py", "--pdf_dir", "s3://d4bl-switchboard-data", "--es_host", "http://elasticsearch:9200", "--verbose"] 