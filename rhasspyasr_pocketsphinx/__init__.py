"""Automated speech recognition in Rhasspy using Pocketsphinx."""
from .train import PronunciationsType, guess_pronunciations, read_dict, train
from .transcribe import PocketsphinxTranscriber
