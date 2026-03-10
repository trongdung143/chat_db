FROM python:3.12.12-slim

WORKDIR /app

RUN pip install uv

COPY requirements.txt .
RUN uv pip install --system -r requirements.txt
COPY . .

# Make port configurable via environment variable
ENV PORT=8080

# Expose the port
EXPOSE $PORT

# Use environment variable for port
CMD uv run uvicorn src.main:app --host 0.0.0.0 --port $PORT