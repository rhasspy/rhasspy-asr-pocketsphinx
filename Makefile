SHELL := bash

PYTHON_NAME = rhasspyasr_pocketsphinx
PYTHON_FILES = $(PYTHON_NAME)/*.py *.py

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

venv: pocketsphinx-python.tar.gz mitlm-0.4.2-$(architecture).tar.gz phonetisaurus-2019-$(architecture).tar.gz
	rm -rf .venv/ $(PYTHON_NAME)/estimate-ngram $(PYTHON_NAME)/phonetisaurus-* $(PYTHON_NAME)/*.so*
	python3 -m venv .venv
	.venv/bin/pip3 install --upgrade pip
	.venv/bin/pip3 install wheel setuptools
	.venv/bin/pip3 install pocketsphinx-python.tar.gz
	.venv/bin/pip3 install -r requirements.txt
	.venv/bin/pip3 install -r requirements_dev.txt
	tar -C $(PYTHON_NAME)/ -xvf mitlm-0.4.2-$(architecture).tar.gz \
      --strip-components=2 \
      mitlm/bin/estimate-ngram mitlm/lib/libmitlm.so.1
	patchelf --set-rpath '$ORIGIN' $(PYTHON_NAME)/estimate-ngram
	tar -C $(PYTHON_NAME)/ -xvf phonetisaurus-2019-$(architecture).tar.gz \
	  --strip-components=2 \
      ./bin/phonetisaurus-apply ./bin/phonetisaurus-g2pfst \
      ./lib/libfst.so.13.0.0 ./lib/libfstfar.so.13.0.0 ./lib/libfstngram.so.13.0.0
	mv $(PYTHON_NAME)/libfst.so.13.0.0 $(PYTHON_NAME)/libfst.so.13
	mv $(PYTHON_NAME)/libfstfar.so.13.0.0 $(PYTHON_NAME)/libfstfar.so.13
	mv $(PYTHON_NAME)/libfstngram.so.13.0.0 $(PYTHON_NAME)/libfstngram.so.13
	patchelf --set-rpath '$ORIGIN' $(PYTHON_NAME)/libfstfar.so.13
	patchelf --set-rpath '$ORIGIN' $(PYTHON_NAME)/libfstngram.so.13
	patchelf --set-rpath '$ORIGIN' $(PYTHON_NAME)/phonetisaurus-g2pfst

dist:
	rm -rf dist/
	python3 setup.py bdist_wheel --plat-name $(platform)

# -----------------------------------------------------------------------------
# Downloads
# -----------------------------------------------------------------------------

# Download Python Pocketsphinx library with no dependency on PulseAudio.
pocketsphinx-python.tar.gz:
	curl -sSfL -o $@ 'https://github.com/synesthesiam/pocketsphinx-python/releases/download/v1.0/pocketsphinx-python.tar.gz'

# Download pre-built MITLM binaries.
mitlm-0.4.2-$(architecture).tar.gz:
	curl -sSfL -o $@ "https://github.com/synesthesiam/docker-mitlm/releases/download/v0.4.2/mitlm-0.4.2-$(architecture).tar.gz"

# Download pre-built Phonetisaurus binaries.
phonetisaurus-2019-$(architecture).tar.gz:
	curl -sSfL -o $@ "https://github.com/synesthesiam/docker-phonetisaurus/releases/download/v2019.1/phonetisaurus-2019-$(architecture).tar.gz"
