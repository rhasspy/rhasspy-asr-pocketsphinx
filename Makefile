SHELL := bash

PYTHON_NAME = rhasspyasr_pocketsphinx
PYTHON_FILES = $(PYTHON_NAME)/*.py *.py
DOWNLOAD_DIR = download

architecture := $(shell bash architecture.sh)
platform = $(shell sh platform.sh)

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

venv: $(DOWNLOAD_DIR)/pocketsphinx-python.tar.gz $(DOWNLOAD_DIR)/mitlm-0.4.2-$(architecture).tar.gz $(DOWNLOAD_DIR)/phonetisaurus-2019-$(architecture).tar.gz
	scripts/create-venv.sh

dist:
	rm -rf dist/
	python3 setup.py bdist_wheel --plat-name $(platform)

# -----------------------------------------------------------------------------
# Downloads
# -----------------------------------------------------------------------------

# Download Python Pocketsphinx library with no dependency on PulseAudio.
$(DOWNLOAD_DIR)/pocketsphinx-python.tar.gz:
	curl -sSfL -o $@ 'https://github.com/synesthesiam/pocketsphinx-python/releases/download/v1.0/pocketsphinx-python.tar.gz'

# Download pre-built MITLM binaries.
$(DOWNLOAD_DIR)/mitlm-0.4.2-$(architecture).tar.gz:
	curl -sSfL -o $@ "https://github.com/synesthesiam/docker-mitlm/releases/download/v0.4.2/mitlm-0.4.2-$(architecture).tar.gz"

# Download pre-built Phonetisaurus binaries.
$(DOWNLOAD_DIR)/phonetisaurus-2019-$(architecture).tar.gz:
	curl -sSfL -o $@ "https://github.com/synesthesiam/docker-phonetisaurus/releases/download/v2019.1/phonetisaurus-2019-$(architecture).tar.gz"
