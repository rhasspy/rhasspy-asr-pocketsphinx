"""Command-line interface to rhasspy-asr-pocketsphinx"""
import argparse
import dataclasses
import json
import logging
import os
import sys
import typing
import wave
from pathlib import Path

import rhasspynlu
from rhasspynlu.g2p import PronunciationsType

from . import PocketsphinxTranscriber
from .train import train as pocketsphinx_train

_LOGGER = logging.getLogger(__name__)

# -----------------------------------------------------------------------------


def main():
    """Main method."""
    args = get_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    _LOGGER.debug(args)

    # Dispatch to appropriate sub-command
    args.func(args)


# -----------------------------------------------------------------------------


def get_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(prog="rhasspy-asr-pocketsphinx")
    parser.add_argument(
        "--debug", action="store_true", help="Print DEBUG messages to the console"
    )

    # Create subparsers for each sub-command
    sub_parsers = parser.add_subparsers()
    sub_parsers.required = True
    sub_parsers.dest = "command"

    # -------------------------------------------------------------------------

    # Transcribe settings
    transcribe_parser = sub_parsers.add_parser(
        "transcribe", help="Do speech to text on one or more WAV files"
    )
    transcribe_parser.set_defaults(func=transcribe)

    transcribe_parser.add_argument(
        "wav_file", nargs="*", help="WAV file(s) to transcribe"
    )
    transcribe_parser.add_argument(
        "--acoustic-model",
        required=True,
        help="Path to Pocketsphinx acoustic model directory (hmm)",
    )
    transcribe_parser.add_argument(
        "--dictionary", required=True, help="Path to pronunciation dictionary file"
    )
    transcribe_parser.add_argument(
        "--language-model", required=True, help="Path to ARPA language model file"
    )
    transcribe_parser.add_argument(
        "--mllr-matrix", default=None, help="Path to tuned MLLR matrix file"
    )

    # -------------------------------------------------------------------------

    # Train settings
    train_parser = sub_parsers.add_parser(
        "train", help="Generate dictionary/language model from intent graph"
    )
    train_parser.set_defaults(func=train)
    train_parser.add_argument(
        "--intent-graph", help="Path to intent graph JSON file (default: stdin)"
    )
    train_parser.add_argument(
        "--dictionary",
        required=True,
        help="Path to write custom pronunciation dictionary",
    )
    train_parser.add_argument(
        "--dictionary-casing",
        choices=["upper", "lower", "ignore"],
        default="ignore",
        help="Case transformation for dictionary words (training, default: ignore)",
    )
    train_parser.add_argument(
        "--language-model", help="Path to write custom language model"
    )
    train_parser.add_argument(
        "--base-dictionary",
        action="append",
        required=True,
        help="Paths to pronunciation dictionaries",
    )
    train_parser.add_argument(
        "--g2p-model", help="Path to Phonetisaurus grapheme-to-phoneme FST model"
    )
    train_parser.add_argument(
        "--g2p-casing",
        choices=["upper", "lower", "ignore"],
        default="ignore",
        help="Case transformation for g2p words (training, default: ignore)",
    )

    return parser.parse_args()


# -----------------------------------------------------------------------------


def transcribe(args: argparse.Namespace):
    """Transcribes WAV file(s)"""
    # Load transcriber
    args.acoustic_model = Path(args.acoustic_model)
    args.dictionary = Path(args.dictionary)
    args.language_model = Path(args.language_model)

    if args.mllr_matrix:
        args.mllr_matrix = Path(args.mllr_matrix)

    transcriber = PocketsphinxTranscriber(
        args.acoustic_model,
        args.dictionary,
        args.language_model,
        mllr_matrix=args.mllr_matrix,
        debug=args.debug,
    )

    try:
        if args.wav_file:
            # Transcribe WAV files
            for wav_path in args.wav_file:
                _LOGGER.debug("Processing %s", wav_path)
                wav_bytes = open(wav_path, "rb").read()
                result = transcriber.transcribe_wav(wav_bytes)
                print_json(result)
        else:
            # Read WAV data from stdin
            if os.isatty(sys.stdin.fileno()):
                print("Reading WAV data from stdin...", file=sys.stderr)

            # Stream in chunks
            with wave.open(sys.stdin.buffer, "rb") as wav_file:

                def audio_stream(wav_file, frames_in_chunk):
                    num_frames = wav_file.getnframes()
                    try:
                        while num_frames > frames_in_chunk:
                            yield wav_file.readframes(frames_in_chunk)
                            num_frames -= frames_in_chunk

                        if num_frames > 0:
                            # Last chunk
                            yield wav_file.readframes(num_frames)
                    except KeyboardInterrupt:
                        pass

                result = transcriber.transcribe_stream(
                    audio_stream(wav_file, args.frames_in_chunk),
                    wav_file.getframerate(),
                    wav_file.getsampwidth(),
                    wav_file.getnchannels(),
                )

                print_json(result)
    except KeyboardInterrupt:
        pass
    finally:
        transcriber.stop()


# -----------------------------------------------------------------------------


def train(args: argparse.Namespace):
    """Generates dictionary and language model from intent graph."""
    if args.dictionary:
        args.dictionary = Path(args.dictionary)

    if args.language_model:
        args.language_model = Path(args.language_model)

    if args.g2p_model:
        args.g2p_model = Path(args.g2p_model)

    args.base_dictionary = [Path(p) for p in args.base_dictionary]

    if args.intent_graph:
        # Load graph from file
        args.intent_graph = Path(args.intent_graph)

        _LOGGER.debug("Loading intent graph from %s", args.intent_graph)
        with open(args.intent_graph, "r") as graph_file:
            graph_dict = json.load(graph_file)
    else:
        # Load graph from stdin
        if os.isatty(sys.stdin.fileno()):
            print("Reading intent graph from stdin...", file=sys.stderr)

        graph_dict = json.load(sys.stdin)

    pronunciations: PronunciationsType = {}
    for dict_path in args.base_dictionary:
        if os.path.exists(dict_path):
            _LOGGER.debug("Loading dictionary %s", str(dict_path))
            rhasspynlu.g2p.read_pronunciations(dict_path, pronunciations)

    pocketsphinx_train(
        graph_dict,
        args.dictionary,
        args.language_model,
        pronunciations,
        dictionary_word_transform=get_word_transform(args.dictionary_casing),
        g2p_model=args.g2p_model,
        g2p_word_transform=get_word_transform(args.g2p_casing),
    )


def get_word_transform(name: str) -> typing.Callable[[str], str]:
    """Gets a word transformation function by name."""
    if name == "upper":
        return str.upper

    if name == "lower":
        return str.lower

    return lambda s: s


# -----------------------------------------------------------------------------


def print_json(result):
    """Print data class as JSON"""
    json.dump(dataclasses.asdict(result), sys.stdout, ensure_ascii=False)
    print("")


# -----------------------------------------------------------------------------

if __name__ == "__main__":
    main()
