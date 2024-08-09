.PHONY: install
install:
	poetry install
	poetry run python install_nltk_packages.py

.PHONY: update
update:
	poetry update

.PHONY: lint
lint:
	poetry run flake8
	poetry run black --check app/

.PHONY: format
format:
	poetry run black app/
	poetry run isort app/

.PHONY: test
test:
	mkdir -p logs/
	poetry run pytest tests/

