################################################################################

PROJECT_NAME = gdrive-suite
PYTHON_VERSION = 3.13
PYTHON_INTERPRETER = python

################################################################################
.PHONY: .venv
	uv sync --upgrade
	source .venv/bin/activate

.PHONY: pre-commit
pre-commit: .venv
	uvx ruff check . --fix --exit-non-zero-on-fix
	uvx ruff format src

.PHONY: clean
clean:
	find . -type f -name "*.py[col]" -delete
	find . -type f -name "__pycache__" -delete

.PHONY: install
	uv pip install -e "."
	uv pip install -e ".[dev]"

