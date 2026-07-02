.PHONY: start stop logs build dev-backend dev-frontend

start:
	docker compose up -d

stop:
	docker compose down

logs:
	docker compose logs -f

build:
	docker compose build

# --- local development (without Docker) ---

dev-backend:
	PYTHONPATH=. venv311/bin/python backend/run.py

dev-frontend:
	cd frontend && npm start
