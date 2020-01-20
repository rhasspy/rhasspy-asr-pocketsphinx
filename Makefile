PYTHON_FILES = rhasspyasr_pocketsphinx/*.py *.py

.PHONY: reformat check venv dist

reformat:
	black .
	isort $(PYTHON_FILES)

check:
	flake8 $(PYTHON_FILES)
	pylint $(PYTHON_FILES)
	mypy $(PYTHON_FILES)
	black --check .
	isort --check-only $(PYTHON_FILES)
	yamllint .
	pip list --outdated

venv: pocketsphinx-python.tar.gz
	rm -rf .venv/
	python3 -m venv .venv
	.venv/bin/pip3 install --upgrade pip
	.venv/bin/pip3 install wheel setuptools
	.venv/bin/pip3 install pocketsphinx-python.tar.gz
	.venv/bin/pip3 install -r requirements.txt
	.venv/bin/pip3 install -r requirements_dev.txt

dist:
	python3 setup.py sdist

# -----------------------------------------------------------------------------
# Downloads
# -----------------------------------------------------------------------------

# Download Python Pocketsphinx library with no dependency on PulseAudio.
pocketsphinx-python.tar.gz:
	curl -sSfL -o $@ 'https://github.com/synesthesiam/pocketsphinx-python/releases/download/v1.0/pocketsphinx-python.tar.gz'
