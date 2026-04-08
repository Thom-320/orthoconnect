PYTHON := .venv/bin/python
PIP := .venv/bin/pip

.PHONY: setup reset-db test cli gui

setup:
	python3 -m venv .venv
	$(PIP) install -r requirements.txt

reset-db:
	PYTHONPATH=. $(PYTHON) scripts/reset_db.py

test:
	PYTHONPATH=. $(PYTHON) -m unittest discover -s tests -v

cli:
	PYTHONPATH=. $(PYTHON) -m src.main

gui:
	PYTHONPATH=. $(PYTHON) -m src.gui_main
