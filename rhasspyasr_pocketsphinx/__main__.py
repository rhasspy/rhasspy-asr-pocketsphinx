"""Command-line interface to rhasspy-asr-pocketsphinx"""
import argparse
import logging
import sys
import json
import os
import wave
from pathlib import Path

import attr

from . import PocketsphinxTranscriber

_LOGGER = logging.getLogger(__name__)


def main():
    """Main method"""
    parser = argparse.ArgumentParser("rhasspyasr_kaldi")
    parser.add_argument("wav_file", nargs="*", help="WAV file(s) to transcribe")
    parser.add_argument(
        "--acoustic-model",
        required=True,
        help="Path to Pocketsphinx acoustic model directory (hmm)",
    )
    parser.add_argument(
        "--dictionary", required=True, help="Path to pronunciation dictionary file"
    )
    parser.add_argument(
        "--language-model", required=True, help="Path to ARPA language model file"
    )
    parser.add_argument(
        "--mllr-matrix", default=None, help="Path to tuned MLLR matrix file"
    )
    parser.add_argument(
        "--no-stream", action="store_true", help="Process entire WAV file"
    )
    parser.add_argument(
        "--frames-in-chunk",
        type=int,
        default=1024,
        help="Number of frames to process at a time",
    )
    parser.add_argument(
        "--debug", action="store_true", help="Print DEBUG messages to console"
    )
    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    _LOGGER.debug(args)

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


# -----------------------------------------------------------------------------


def print_json(result):
    """Print attr class as JSON"""
    json.dump(attr.asdict(result), sys.stdout)
    print("")


# -----------------------------------------------------------------------------

if __name__ == "__main__":
    main()
