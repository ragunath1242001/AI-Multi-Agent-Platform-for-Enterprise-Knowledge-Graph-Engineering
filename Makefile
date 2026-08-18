.PHONY: install dev streamlit test lint format docker-up docker-down

install:
	cd backend && python -m pip install -e ".[dev]"
	cd agents && python -m pip install -e ".[dev]"
	python -m pip install -r streamlit_app/requirements.txt
	cd frontend && pnpm install

dev:
	docker compose up --build

streamlit:
	streamlit run streamlit_app/app.py

test:
	cd backend && pytest
	cd agents && pytest
	cd frontend && pnpm test

lint:
	cd backend && ruff check app tests
	cd agents && ruff check semanticops_agents tests
	cd frontend && pnpm lint

format:
	cd backend && ruff format app tests
	cd agents && ruff format semanticops_agents tests
	cd frontend && pnpm format

docker-up:
	docker compose up -d --build

docker-down:
	docker compose down
