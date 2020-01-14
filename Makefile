PYTHON_FILES = rhasspyasr_pocketsphinx/*.py *.py

.PHONY: check venv dist

check:
	flake8 $(PYTHON_FILES)
	pylint $(PYTHON_FILES)
	mypy $(PYTHON_FILES)

venv:
	rm -rf .venv/
	python3 -m venv .venv
	.venv/bin/pip3 install wheel setuptools
	.venv/bin/pip3 install -r requirements.txt
	.venv/bin/pip3 install -r requirements_dev.txt

dist:
	python3 setup.py sdist
