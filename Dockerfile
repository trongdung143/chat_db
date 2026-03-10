FROM python:3.12.12-slim

WORKDIR /app

ENV DEBIAN_FRONTEND=noninteractive
ENV ACCEPT_EULA=Y

RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    gcc \
    g++ \
    unixodbc \
    unixodbc-dev \
    && rm -rf /var/lib/apt/lists/*

RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && curl https://packages.microsoft.com/config/debian/12/prod.list \
    > /etc/apt/sources.list.d/mssql-release.list

RUN apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql18

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