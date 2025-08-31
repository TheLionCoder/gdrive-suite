################################################################################

PROJECT_NAME = gdrive-suite
PYTHON_VERSION = 3.13
PYTHON_INTERPRETER = python

################################################################################

.PHONY: clean
clean:
	find . -type f -name "*.py[col]" -delete
	find . -type f -name "__pycache__" -delete
