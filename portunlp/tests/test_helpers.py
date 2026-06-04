from typing import Any

import pytest

spacy: Any = pytest.importorskip("spacy")
pytest.importorskip("pt_core_news_sm")

from portunlp import spacy_lemmatize, spacy_pos_tag, spacy_tokenize  # noqa: E402


@pytest.fixture(scope="module")
def sample_text() -> str:
    """Provide a sample Portuguese sentence for spaCy helpers."""
    return "Os gatos bonitos comem peixe."


def test_spacy_tokenize(sample_text: str) -> None:
    """spaCy tokenizer returns at least two tokens."""
    tokens = spacy_tokenize(sample_text)
    assert isinstance(tokens, list)
    assert len(tokens) >= 2


def test_spacy_lemmatize(sample_text: str) -> None:
    """spaCy lemmatizer yields lemmas for each word."""
    lemmas = spacy_lemmatize(sample_text)
    assert isinstance(lemmas, list)
    assert len(lemmas) == len(sample_text.split())


def test_spacy_pos_tag(sample_text: str) -> None:
    """spaCy POS tagger emits a tag for each word."""
    tags = spacy_pos_tag(sample_text)
    assert isinstance(tags, list)
    assert len(tags) == len(sample_text.split())


def test_tokenize_empty() -> None:
    """Tokenizing empty input returns an empty list."""
    assert spacy_tokenize("") == []


def test_lemmatize_empty() -> None:
    """Lemmatizing empty input returns an empty list."""
    assert spacy_lemmatize("") == []


def test_pos_tag_empty() -> None:
    """POS tagging empty input returns an empty list."""
    assert spacy_pos_tag("") == []
