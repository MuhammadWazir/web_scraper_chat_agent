# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast dependency management
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin/:$PATH"

# Set the working directory in the container
WORKDIR /app

# Copy the dependency files first
COPY pyproject.toml uv.lock ./

# Install dependencies using uv
RUN uv sync --frozen


RUN uv run playwright install --with-deps chromium

# Copy the rest of the application code
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Make the entrypoint script executable
RUN chmod +x entrypoint.sh

# Expose the port
EXPOSE 8000

# Command to run the application
CMD ["./entrypoint.sh"]