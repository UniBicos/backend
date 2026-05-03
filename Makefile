run:
	python manage.py runserver

migrations:
	python manage.py makemigrations

migrate:
	python manage.py migrate

seed-superuser:
	python manage.py seed_superuser $(ARGS)

format:
	ruff format .

lint:
	ruff check .

fix:
	ruff check . --fix
	ruff format .