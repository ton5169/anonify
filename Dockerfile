FROM python:3.13-slim
COPY --from=ghcr.io/astral-sh/uv:0.9.5 /uv /uvx /bin/

WORKDIR /backend
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-cache

COPY /backend .
ENV PYTHONPATH=/backend
EXPOSE 8000

CMD ["uv", "run", "uvicorn", "app.api.server:app", "--reload", "--workers", "1", "--host", "0.0.0.0", "--port", "8000"]
