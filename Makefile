run:
	python manage.py runserver

migrations:
	python manage.py makemigrations

migrate:
	python manage.py migrate

format:
	ruff format .

lint:
	ruff check .

fix:
	ruff check . --fix
	ruff format .