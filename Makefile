.PHONY: run

run: venv
	venv/bin/python3 main.py

venv: requirements.txt
	python3 -m venv venv
	venv/bin/pip install -r requirements.txt
