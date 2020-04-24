"""Methods for generating ASR artifacts."""
import logging
import shutil
import tempfile
import typing
from pathlib import Path

import networkx as nx
import rhasspynlu
from rhasspynlu.g2p import PronunciationsType

_DIR = Path(__file__).parent
_LOGGER = logging.getLogger(__name__)

# -------------------------------------------------------------------


def train(
    graph: nx.DiGraph,
    dictionary: typing.Union[str, Path],
    language_model: typing.Union[str, Path],
    pronunciations: PronunciationsType,
    dictionary_word_transform: typing.Optional[typing.Callable[[str], str]] = None,
    g2p_model: typing.Optional[typing.Union[str, Path]] = None,
    g2p_word_transform: typing.Optional[typing.Callable[[str], str]] = None,
    missing_words_path: typing.Optional[typing.Union[str, Path]] = None,
    vocab_path: typing.Optional[typing.Union[str, Path]] = None,
    language_model_fst: typing.Optional[typing.Union[str, Path]] = None,
    base_language_model_fst: typing.Optional[typing.Union[str, Path]] = None,
    base_language_model_weight: typing.Optional[float] = None,
    mixed_language_model_fst: typing.Optional[typing.Union[str, Path]] = None,
    balance_counts: bool = True,
):
    """Re-generates language model and dictionary from intent graph"""
    vocabulary: typing.Set[str] = set()
    if vocab_path:
        vocab_file = open(vocab_path, "w+")
    else:
        vocab_file = typing.cast(
            typing.TextIO, tempfile.NamedTemporaryFile(suffix=".txt", mode="w+")
        )
        vocab_path = vocab_file.name

    # Language model mixing
    is_mixing = False
    base_fst_weight = None
    if (
        (base_language_model_fst is not None)
        and (base_language_model_weight is not None)
        and (base_language_model_weight > 0)
    ):
        is_mixing = True
        base_fst_weight = (base_language_model_fst, base_language_model_weight)

    # Begin training
    with tempfile.NamedTemporaryFile(mode="w+") as lm_file:
        with vocab_file:
            # Create language model
            _LOGGER.debug("Converting to ARPA language model")
            rhasspynlu.arpa_lm.graph_to_arpa(
                graph,
                lm_file.name,
                vocab_path=vocab_path,
                model_path=language_model_fst,
                base_fst_weight=base_fst_weight,
                merge_path=mixed_language_model_fst,
            )

            # Load vocabulary
            vocab_file.seek(0)
            vocabulary.update(line.strip() for line in vocab_file)

            if is_mixing:
                # Add all known words
                vocabulary.update(pronunciations.keys())

        assert vocabulary, "No words in vocabulary"

        # Write dictionary to temporary file
        with tempfile.NamedTemporaryFile(mode="w+") as dictionary_file:
            _LOGGER.debug("Writing pronunciation dictionary")
            rhasspynlu.g2p.write_pronunciations(
                vocabulary,
                pronunciations,
                dictionary_file.name,
                g2p_model=g2p_model,
                g2p_word_transform=g2p_word_transform,
                missing_words_path=missing_words_path,
            )

            # -----------------------------------------------------------------

            # Copy dictionary over real file
            dictionary_file.seek(0)
            shutil.copy(dictionary_file.name, dictionary)
            _LOGGER.debug("Wrote dictionary to %s", str(dictionary))

            # Copy language model over real file
            lm_file.seek(0)
            shutil.copy(lm_file.name, language_model)
            _LOGGER.debug("Wrote language model to %s", str(language_model))
