.PHONY: install lint format test check all

install:
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

lint:
	flake8 cthulhu_src/web tests

format:
	black cthulhu_src tests

test:
	pytest

check:
	python -m cthulhu_src.main --help

all: format lint test check
