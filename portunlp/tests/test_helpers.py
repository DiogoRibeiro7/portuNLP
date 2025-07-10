import pytest
import spacy

if getattr(spacy, "__fake__", False):
    pytest.skip("spaCy not available", allow_module_level=True)

from portunlp import spacy_lemmatize, spacy_pos_tag, spacy_tokenize


@pytest.fixture(scope="module")
def sample_text():
    return "Os gatos bonitos comem peixe."


def test_spacy_tokenize(sample_text):
    tokens = spacy_tokenize(sample_text)
    assert isinstance(tokens, list)
    assert len(tokens) >= 2


def test_spacy_lemmatize(sample_text):
    lemmas = spacy_lemmatize(sample_text)
    assert isinstance(lemmas, list)
    assert len(lemmas) == len(sample_text.split())


def test_spacy_pos_tag(sample_text):
    tags = spacy_pos_tag(sample_text)
    assert isinstance(tags, list)
    assert len(tags) == len(sample_text.split())
