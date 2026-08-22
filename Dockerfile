FROM ghcr.io/astral-sh/uv:0.8.13 AS uv

FROM python:3.13-slim-bookworm

COPY --from=uv /uv /uvx /bin/

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY src ./src

EXPOSE 8080

CMD ["/app/.venv/bin/python", "src/server.py"]
