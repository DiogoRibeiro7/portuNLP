"""spaCy-backed helpers for Portuguese NLP tasks."""

from __future__ import annotations

from importlib import import_module
from typing import TYPE_CHECKING, Any, cast

if TYPE_CHECKING:
    from spacy.language import Language
else:
    Language = Any

SPACY_MODEL_NAME = "pt_core_news_sm"

_nlp: Language | None = None


def _load_model() -> Language:
    """Load the spaCy Portuguese model lazily.

    Returns:
        Language: Loaded spaCy language model.

    Raises:
        OSError: If spaCy or the Portuguese model is not installed.
    """
    global _nlp
    if _nlp is None:
        try:
            spacy_module = import_module("spacy")
            _nlp = cast(Language, spacy_module.load(SPACY_MODEL_NAME))
        except ModuleNotFoundError as exc:
            raise OSError(
                "spaCy is not installed. Run `poetry install` to install Python dependencies."
            ) from exc
        except OSError as exc:
            raise OSError(
                "spaCy Portuguese model not found. "
                f"Run `python -m spacy download {SPACY_MODEL_NAME}`."
            ) from exc
    return _nlp


def _process_text(text: str, attribute: str) -> list[str]:
    """Process text with spaCy and return a token attribute.

    Args:
        text (str): Text to process.
        attribute (str): Token attribute name to extract.

    Returns:
        list[str]: Extracted token values.

    Raises:
        OSError: If spaCy or the Portuguese model is not installed.
    """
    if not text:
        return []

    doc = _load_model()(text)
    return [getattr(token, attribute) for token in doc]


def spacy_tokenize(text: str) -> list[str]:
    """Tokenize text using spaCy.

    Args:
        text (str): Text to tokenize.

    Returns:
        list[str]: List of token strings.

    Raises:
        OSError: If spaCy or the Portuguese model is not installed.
    """
    return _process_text(text, "text")


def spacy_lemmatize(text: str) -> list[str]:
    """Lemmatize text using spaCy.

    Args:
        text (str): Text to lemmatize.

    Returns:
        list[str]: List of lemma strings.

    Raises:
        OSError: If spaCy or the Portuguese model is not installed.
    """
    return _process_text(text, "lemma_")


def spacy_pos_tag(text: str) -> list[str]:
    """Generate POS tags using spaCy.

    Args:
        text (str): Text to tag.

    Returns:
        list[str]: List of part-of-speech tags.

    Raises:
        OSError: If spaCy or the Portuguese model is not installed.
    """
    return _process_text(text, "pos_")
