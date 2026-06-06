from typing import Any

import pytest

spacy: Any = pytest.importorskip("spacy")
pytest.importorskip("pt_core_news_sm")

from portunlp import (  # noqa: E402
    spacy_analyze,
    spacy_corpus,
    spacy_document,
    spacy_dependencies,
    spacy_entities,
    spacy_lemmatize,
    spacy_morphology,
    spacy_noun_chunks,
    spacy_pos_tag,
    spacy_sentences,
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


def test_spacy_dependencies(sample_text: str) -> None:
    """spaCy dependency summary returns relation metadata."""
    summary = spacy_dependencies(sample_text)
    assert summary.tokens
    assert isinstance(summary.root, str)
    assert isinstance(summary.dep_counts, dict)


def test_spacy_noun_chunks(sample_text: str) -> None:
    """spaCy noun-chunk summary returns chunk metadata."""
    summary = spacy_noun_chunks(sample_text)
    assert isinstance(summary.chunks, list)
    assert isinstance(summary.root_counts, dict)


def test_spacy_sentences(sample_text: str) -> None:
    """spaCy sentence summary returns sentence metadata."""
    summary = spacy_sentences(sample_text)
    assert isinstance(summary.sentences, list)
    assert summary.sentence_count >= 1


def test_spacy_document(sample_text: str) -> None:
    """spaCy document summary returns all major analysis sections."""
    summary = spacy_document(sample_text)
    assert summary.tokens
    assert summary.morphology.tokens
    assert isinstance(summary.entities.label_counts, dict)
    assert isinstance(summary.dependencies.dep_counts, dict)
    assert isinstance(summary.noun_chunks.root_counts, dict)
    assert summary.sentences.sentence_count >= 1


def test_spacy_corpus(sample_text: str) -> None:
    """spaCy corpus summary returns per-document and aggregate metadata."""
    summary = spacy_corpus([sample_text, sample_text])
    assert len(summary.documents) == 2
    assert summary.document_count == 2
    assert summary.token_count >= 2
    assert isinstance(summary.pos_counts, dict)
    assert isinstance(summary.entity_label_counts, dict)
    assert isinstance(summary.dependency_counts, dict)
    assert isinstance(summary.noun_chunk_root_counts, dict)


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


def test_dependencies_empty() -> None:
    """Dependency analysis of empty input returns empty structures."""
    summary = spacy_dependencies("")
    assert summary.tokens == []
    assert summary.root == ""
    assert summary.dep_counts == {}


def test_noun_chunks_empty() -> None:
    """Noun-chunk analysis of empty input returns empty structures."""
    summary = spacy_noun_chunks("")
    assert summary.chunks == []
    assert summary.root_counts == {}


def test_sentences_empty() -> None:
    """Sentence analysis of empty input returns empty structures."""
    summary = spacy_sentences("")
    assert summary.sentences == []
    assert summary.sentence_count == 0


def test_document_empty() -> None:
    """Document analysis of empty input returns empty structures."""
    summary = spacy_document("")
    assert summary.text == ""
    assert summary.tokens == []
    assert summary.morphology.tokens == []
    assert summary.entities.entities == []
    assert summary.dependencies.tokens == []
    assert summary.noun_chunks.chunks == []
    assert summary.sentences.sentences == []


def test_corpus_empty() -> None:
    """Corpus analysis of empty input returns empty structures."""
    summary = spacy_corpus([])
    assert summary.documents == []
    assert summary.document_count == 0
    assert summary.token_count == 0
    assert summary.pos_counts == {}
    assert summary.entity_label_counts == {}
    assert summary.dependency_counts == {}
    assert summary.noun_chunk_root_counts == {}
