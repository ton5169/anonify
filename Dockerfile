FROM python:3.13-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:0.9.5 /uv /uvx /bin/

WORKDIR /backend

# Copy only dependency files to leverage Docker cache
COPY pyproject.toml uv.lock ./

# Install dependencies in separate folder to access it not dependant on the source code
ENV UV_PROJECT_ENVIRONMENT=/opt/venv
RUN uv sync --frozen --no-dev

# Copy the source code
COPY backend/ .

# Copy environment file used by Config
COPY backend/.env ./.env

# Set environment variables
ENV PYTHONPATH=/backend
ENV PATH="/opt/venv/bin:$PATH"

EXPOSE 8000

# Start the application
CMD ["uv", "run", "--group", "prod", "uvicorn", "app.api.server:app", "--reload", "--workers", "1", "--host", "0.0.0.0", "--port", "8000"]



# docker build -t anonify .
# docker run -p 8000:8000 anonify:latest
