.PHONY: check venv dist

check:
	flake8 rhasspyasr_pocketsphinx/*.py
	pylint rhasspyasr_pocketsphinx/*.py
	mypy rhasspyasr_pocketsphinx/*.py

venv:
	rm -rf .venv/
	python3 -m venv .venv
	.venv/bin/pip3 install wheel setuptools
	.venv/bin/pip3 install -r requirements_all.txt

dist:
	python3 setup.py sdist
