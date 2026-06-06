from typing import Any

import pytest

spacy: Any = pytest.importorskip("spacy")
pytest.importorskip("pt_core_news_sm")

from portunlp import (  # noqa: E402
    spacy_analyze,
    spacy_entities,
    spacy_lemmatize,
    spacy_morphology,
    spacy_pos_tag,
    spacy_sentencize,
    spacy_tokenize,
)


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


def test_spacy_sentencize(sample_text: str) -> None:
    """spaCy sentence segmentation emits at least one sentence."""
    sentences = spacy_sentencize(sample_text)
    assert isinstance(sentences, list)
    assert len(sentences) >= 1


def test_spacy_analyze(sample_text: str) -> None:
    """spaCy structured analysis returns token metadata."""
    tokens = spacy_analyze(sample_text)
    assert isinstance(tokens, list)
    assert len(tokens) >= 1
    assert tokens[0].text
    assert isinstance(tokens[0].is_alpha, bool)


def test_spacy_morphology(sample_text: str) -> None:
    """spaCy morphology summary returns token and count metadata."""
    summary = spacy_morphology(sample_text)
    assert summary.tokens
    assert isinstance(summary.pos_counts, dict)
    assert isinstance(summary.morph_counts, dict)
    assert summary.lemmas


def test_spacy_entities(sample_text: str) -> None:
    """spaCy entity summary returns entity and label metadata."""
    summary = spacy_entities(sample_text)
    assert isinstance(summary.entities, list)
    assert isinstance(summary.label_counts, dict)


def test_tokenize_empty() -> None:
    """Tokenizing empty input returns an empty list."""
    assert spacy_tokenize("") == []


def test_lemmatize_empty() -> None:
    """Lemmatizing empty input returns an empty list."""
    assert spacy_lemmatize("") == []


def test_pos_tag_empty() -> None:
    """POS tagging empty input returns an empty list."""
    assert spacy_pos_tag("") == []


def test_sentencize_empty() -> None:
    """Sentence segmentation of empty input returns an empty list."""
    assert spacy_sentencize("") == []


def test_analyze_empty() -> None:
    """Structured analysis of empty input returns an empty list."""
    assert spacy_analyze("") == []


def test_morphology_empty() -> None:
    """Morphology analysis of empty input returns empty structures."""
    summary = spacy_morphology("")
    assert summary.tokens == []
    assert summary.lemmas == []
    assert summary.pos_counts == {}
    assert summary.morph_counts == {}


def test_entities_empty() -> None:
    """Entity analysis of empty input returns empty structures."""
    summary = spacy_entities("")
    assert summary.entities == []
    assert summary.label_counts == {}
