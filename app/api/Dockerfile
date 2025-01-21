FROM python:3.12-slim

WORKDIR /app

# Install curl for healthcheck
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the API code
COPY . .

# Add this line to make Python treat the directory as a package
ENV PYTHONPATH=/app

# For debugging
RUN ls -la /app

# Make sure we have all required files
RUN python -c "import auth; print('Auth module found')"

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]