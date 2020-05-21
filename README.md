# Rhasspy ASR Pocketsphinx

[![Continous Integration](https://github.com/rhasspy/rhasspy-asr-pocketsphinx/workflows/Tests/badge.svg)](https://github.com/rhasspy/rhasspy-asr-pocketsphinx/actions)
[![PyPI package version](https://img.shields.io/pypi/v/rhasspy-asr-pocketsphinx.svg)](https://pypi.org/project/rhasspy-asr-pocketsphinx)
[![Python versions](https://img.shields.io/pypi/pyversions/rhasspy-asr-pocketsphinx.svg)](https://www.python.org)
[![GitHub license](https://img.shields.io/github/license/rhasspy/rhasspy-asr-pocketsphinx.svg)](https://github.com/rhasspy/rhasspy-asr-pocketsphinx/blob/master/LICENSE)

Automated speech recognition in [Rhasspy](https://github.com/synesthesiam/rhasspy) voice assistant with [Pocketsphinx](https://github.com/cmusphinx/pocketsphinx).

## Dependencies

`rhasspy-asr-pocketsphinx` requires:

* Python 3.7
* [Pocketsphinx](https://github.com/cmusphinx/pocketsphinx)
* [Opengrm](http://www.opengrm.org/twiki/bin/view/GRM/NGramLibrary)
* [Phonetisaurus](https://github.com/AdolfVonKleist/Phonetisaurus)

See [pre-built apps](https://github.com/synesthesiam/prebuilt-apps) for pre-compiled binaries.

Pocketsphinx is installed using `pip` from a [fork of the Python library](https://github.com/synesthesiam/pocketsphinx-python) that removes PulseAudio.

## Building From Source

`rhasspy-asr-pocketsphinx` depends on the following programs that must be compiled:

### Phonetisaurus

Make sure you have the necessary dependencies installed:

```bash
sudo apt-get install build-essential
```

First, download and build [OpenFST 1.6.2](http://www.openfst.org/)

```bash
wget http://www.openfst.org/twiki/pub/FST/FstDownload/openfst-1.6.2.tar.gz
tar -xvf openfst-1.6.2.tar.gz
cd openfst-1.6.2
./configure \
    "--prefix=$(pwd)/build" \
    --enable-static --enable-shared \
    --enable-far --enable-ngram-fsts
make
make install
```

Use `make -j 4` if you have multiple CPU cores. This will take a **long** time.

Next, download and extract Phonetisaurus:

```bash
wget -O phonetisaurus-master.tar.gz \
    'https://github.com/AdolfVonKleist/Phonetisaurus/archive/master.tar.gz'
tar -xvf phonetisaurus-master.tar.gz
```

Finally, build Phonetisaurus (where `/path/to/openfst` is the `openfst-1.6.2` directory from above):

```
cd Phonetisaurus-master
./configure \
    --with-openfst-includes=/path/to/openfst/build/include \
    --with-openfst-libs=/path/to/openfst/build/lib
make
make install
```

Use `make -j 4` if you have multiple CPU cores. This will take a **long** time.

You should now be able to run the `phonetisaurus-align` program.

See [docker-phonetisaurus](https://github.com/synesthesiam/docker-phonetisaurus) for a Docker build script.
