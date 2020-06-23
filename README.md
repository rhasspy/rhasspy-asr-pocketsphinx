# Rhasspy ASR Pocketsphinx

[![Continous Integration](https://github.com/rhasspy/rhasspy-asr-pocketsphinx/workflows/Tests/badge.svg)](https://github.com/rhasspy/rhasspy-asr-pocketsphinx/actions)
[![PyPI package version](https://img.shields.io/pypi/v/rhasspy-asr-pocketsphinx.svg)](https://pypi.org/project/rhasspy-asr-pocketsphinx)
[![Python versions](https://img.shields.io/pypi/pyversions/rhasspy-asr-pocketsphinx.svg)](https://www.python.org)
[![GitHub license](https://img.shields.io/github/license/rhasspy/rhasspy-asr-pocketsphinx.svg)](https://github.com/rhasspy/rhasspy-asr-pocketsphinx/blob/master/LICENSE)

Automated speech recognition in [Rhasspy](https://github.com/synesthesiam/rhasspy) voice assistant with [Pocketsphinx](https://github.com/cmusphinx/pocketsphinx).

## Requirements

`rhasspy-asr-pocketsphinx` requires:

* Python 3.7
* [Pocketsphinx](https://github.com/cmusphinx/pocketsphinx)
    * Install as a Python module
* [Opengrm](http://www.opengrm.org/twiki/bin/view/GRM/NGramLibrary)
    * Expects `ngram*` in `$PATH`
* [Phonetisaurus](https://github.com/AdolfVonKleist/Phonetisaurus)
    * Expects `phonetisaurus-apply` in `$PATH`

See [pre-built apps](https://github.com/synesthesiam/prebuilt-apps) for pre-compiled binaries.

Pocketsphinx is installed using `pip` from a [fork of the Python library](https://github.com/synesthesiam/pocketsphinx-python) that removes PulseAudio.

## Installation

```bash
$ git clone https://github.com/rhasspy/rhasspy-asr-pocketsphinx
$ cd rhasspy-asr-pocketsphinx
$ ./configure
$ make
$ make install
```

## Deployment

```bash
$ make dist
```

See `dist/` directory for `.tar.gz` file.
