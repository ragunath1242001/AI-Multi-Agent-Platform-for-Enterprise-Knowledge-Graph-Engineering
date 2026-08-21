FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY agents/pyproject.toml agents/README.md ./agents/
COPY agents/semanticops_agents ./agents/semanticops_agents
RUN pip install --no-cache-dir ./agents

COPY backend/pyproject.toml backend/README.md ./backend/
COPY backend/app ./backend/app
RUN pip install --no-cache-dir -e ./backend

WORKDIR /app/backend

EXPOSE 8000
CMD ["uvicorn", "app.main:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
