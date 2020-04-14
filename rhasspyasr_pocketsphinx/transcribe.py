"""Automated speech recognition in Rhasspy using Pocketsphinx."""
import io
import logging
import os
import time
import typing
import wave
from pathlib import Path

import pocketsphinx
from rhasspyasr import Transcriber, Transcription, TranscriptionToken

_LOGGER = logging.getLogger(__name__)

# -----------------------------------------------------------------------------


class PocketsphinxTranscriber(Transcriber):
    """Speech to text with CMU Pocketsphinx."""

    def __init__(
        self,
        acoustic_model: Path,
        dictionary: Path,
        language_model: Path,
        mllr_matrix: typing.Optional[Path] = None,
        debug: bool = False,
    ):
        self.acoustic_model = acoustic_model
        self.dictionary = dictionary
        self.language_model = language_model
        self.mllr_matrix = mllr_matrix
        self.debug = debug
        self.decoder: typing.Optional[pocketsphinx.Decoder] = None

    def transcribe_wav(self, wav_bytes: bytes) -> typing.Optional[Transcription]:
        """Speech to text from WAV data."""
        if self.decoder is None:
            # Load decoder
            self.decoder = self.get_decoder()

        # Compute WAV duration
        audio_data: bytes = bytes()
        with io.BytesIO(wav_bytes) as wav_buffer:
            with wave.open(wav_buffer) as wav_file:
                frames = wav_file.getnframes()
                rate = wav_file.getframerate()
                wav_duration = frames / float(rate)

                # Extract raw audio data
                audio_data = wav_file.readframes(wav_file.getnframes())

        # Process data as an entire utterance
        start_time = time.perf_counter()
        self.decoder.start_utt()
        self.decoder.process_raw(audio_data, False, True)
        self.decoder.end_utt()

        transcribe_seconds = time.perf_counter() - start_time
        _LOGGER.debug("Decoded audio in %s second(s)", transcribe_seconds)

        hyp = self.decoder.hyp()
        if hyp:
            return Transcription(
                text=hyp.hypstr.strip(),
                likelihood=self.decoder.get_logmath().exp(hyp.prob),
                transcribe_seconds=transcribe_seconds,
                wav_seconds=wav_duration,
                tokens=[
                    TranscriptionToken(
                        token=seg.word,
                        start_time=seg.start_frame / 100,
                        end_time=seg.end_frame / 100,
                        likelihood=self.decoder.get_logmath().exp(seg.prob),
                    )
                    for seg in self.decoder.seg()
                ],
            )

        return None

    def transcribe_stream(
        self,
        audio_stream: typing.Iterable[bytes],
        sample_rate: int,
        sample_width: int,
        channels: int,
    ) -> typing.Optional[Transcription]:
        """Speech to text from an audio stream."""
        assert channels == 1, "Only mono audio supported"
        if self.decoder is None:
            # Load decoder
            self.decoder = self.get_decoder()

        total_frames = 0

        # Process data as an entire utterance
        start_time = time.perf_counter()
        self.decoder.start_utt()

        for frame in audio_stream:
            self.decoder.process_raw(frame, False, False)
            total_frames += 1

        self.decoder.end_utt()

        transcribe_seconds = time.perf_counter() - start_time
        _LOGGER.debug("Decoded audio in %s second(s)", transcribe_seconds)

        hyp = self.decoder.hyp()
        if hyp:
            return Transcription(
                text=hyp.hypstr.strip(),
                likelihood=self.decoder.get_logmath().exp(hyp.prob),
                transcribe_seconds=transcribe_seconds,
                wav_seconds=total_frames / float(sample_rate),
                tokens=[
                    TranscriptionToken(
                        token=seg.word,
                        start_time=seg.start_frame / 100,
                        end_time=seg.end_frame / 100,
                        likelihood=self.decoder.get_logmath().exp(seg.prob),
                    )
                    for seg in self.decoder.seg()
                ],
            )

        return None

    def stop(self):
        """Stop the transcriber."""

    def get_decoder(self) -> pocketsphinx.Decoder:
        """Load Pocketsphinx decoder from command-line arguments."""
        start_time = time.perf_counter()
        decoder_config = pocketsphinx.Decoder.default_config()
        decoder_config.set_string("-hmm", str(self.acoustic_model))
        decoder_config.set_string("-dict", str(self.dictionary))
        decoder_config.set_string("-lm", str(self.language_model))

        if not self.debug:
            decoder_config.set_string("-logfn", os.devnull)

        if (self.mllr_matrix is not None) and self.mllr_matrix.exists():
            decoder_config.set_string("-mllr", str(self.mllr_matrix))

        decoder = pocketsphinx.Decoder(decoder_config)
        end_time = time.perf_counter()

        _LOGGER.debug(
            "Successfully loaded decoder in %s second(s)", end_time - start_time
        )

        return decoder

    def __repr__(self) -> str:
        return (
            "PocketsphinxTranscriber("
            f"acoustic_model={self.acoustic_model})"
            f", dictionary={self.dictionary}"
            f", language_model={self.language_model}"
            f", mllr_matrix={self.mllr_matrix}"
            ")"
        )
