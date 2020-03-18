SHELL := bash

PYTHON_NAME = rhasspyasr_pocketsphinx
PYTHON_FILES = $(PYTHON_NAME)/*.py *.py
DOWNLOAD_DIR = download

architecture := $(shell bash architecture.sh)
platform = $(shell sh platform.sh)

.PHONY: reformat check venv dist downloads

reformat:
	scripts/format-code.sh $(PYTHON_FILES)

check:
	scripts/check-code.sh $(PYTHON_FILES)

venv: downloads
	scripts/create-venv.sh

dist:
	scripts/build-wheel.sh $(platform)

test:
	scripts/run-tests.sh

# -----------------------------------------------------------------------------
# Downloads
# -----------------------------------------------------------------------------

# Rhasspy development dependencies
RHASSPY_DEPS := $(shell grep '^rhasspy-' requirements.txt | sort | comm -3 - rhasspy_wheels.txt | sed -e 's|^|$(DOWNLOAD_DIR)/|' -e 's/==/-/' -e 's/$$/.tar.gz/')

$(DOWNLOAD_DIR)/%.tar.gz:
	mkdir -p "$(DOWNLOAD_DIR)"
	scripts/download-dep.sh "$@"

downloads: $(DOWNLOAD_DIR)/pocketsphinx-python.tar.gz $(DOWNLOAD_DIR)/phonetisaurus-2019-$(architecture).tar.gz $(RHASSPY_DEPS)

# Download Python Pocketsphinx library with no dependency on PulseAudio.
$(DOWNLOAD_DIR)/pocketsphinx-python.tar.gz:
	mkdir -p "$(DOWNLOAD_DIR)"
	curl -sSfL -o $@ 'https://github.com/synesthesiam/pocketsphinx-python/releases/download/v1.0/pocketsphinx-python.tar.gz'

# Download pre-built Phonetisaurus binaries.
$(DOWNLOAD_DIR)/phonetisaurus-2019-$(architecture).tar.gz:
	mkdir -p "$(DOWNLOAD_DIR)"
	curl -sSfL -o $@ "https://github.com/synesthesiam/docker-phonetisaurus/releases/download/v2019.1/phonetisaurus-2019-$(architecture).tar.gz"

# Download pre-built MITLM binaries.
$(DOWNLOAD_DIR)/mitlm-0.4.2-$(architecture).tar.gz:
	mkdir -p "$(DOWNLOAD_DIR)"
	curl -sSfL -o $@ "https://github.com/synesthesiam/docker-mitlm/releases/download/v0.4.2/mitlm-0.4.2-$(architecture).tar.gz"
