FROM python:3.13-alpine

WORKDIR /app

# Install UV, copy the package files, and install dependencies
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
COPY pyproject.toml uv.lock* ./
RUN uv sync --frozen --no-dev

# Copy the application code
COPY . /app/

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "playox.app:app", "--host", "0.0.0.0", "--port", "8000"]
