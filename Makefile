.PHONY: help build up down logs shell migrate createsuperuser test lint clean

help:
	@echo "Django + Podman Development Commands"
	@echo "======================================"
	@echo "build              - Build the Docker image"
	@echo "up                 - Start containers (background)"
	@echo "down               - Stop containers"
	@echo "logs               - View container logs (follow)"
	@echo "shell              - Access Django shell"
	@echo "migrate            - Run database migrations"
	@echo "createsuperuser    - Create admin user"
	@echo "test               - Run tests"
	@echo "lint               - Run code quality checks"
	@echo "clean              - Remove containers and images"
	@echo "deploy             - Deploy to Fly.io"

build:
	podman build -t django-app:latest .

up:
	podman-compose up -d
	@echo "Django app running at http://localhost:8000"

down:
	podman-compose down

logs:
	podman-compose logs -f web

shell:
	podman-compose exec web python manage.py shell

migrate:
	podman-compose exec web python manage.py migrate

makemigrations:
	podman-compose exec web python manage.py makemigrations

createsuperuser:
	podman-compose exec web python manage.py createsuperuser

test:
	podman-compose exec web python manage.py test

lint:
	podman-compose exec web python -m flake8 .

clean:
	podman-compose down -v
	podman rmi django-app:latest

deploy:
	flyctl deploy

deploy-logs:
	flyctl logs

deploy-status:
	flyctl status

deploy-shell:
	flyctl ssh console
