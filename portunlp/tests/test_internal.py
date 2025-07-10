import importlib
import sys
import types

import pytest


@pytest.fixture()
def fake_spacy(monkeypatch):
    """Provide a fake spaCy module for testing."""

    module = types.ModuleType("spacy")

    class DummyToken:
        def __init__(self, text: str) -> None:
            self.text = text
            self.lemma_ = text.lower()
            self.pos_ = "NOUN"

    class DummyNLP:
        def __call__(self, text: str):
            return [DummyToken(t) for t in text.split()]

    calls = {"count": 0}

    def load(name: str):
        calls["count"] += 1
        return DummyNLP()

    module.load = load
    monkeypatch.setitem(sys.modules, "spacy", module)
    portunlp = importlib.reload(importlib.import_module("portunlp"))
    portunlp._nlp = None
    return portunlp, calls


def test_load_model_caches(fake_spacy):
    portunlp, calls = fake_spacy
    portunlp.spacy_tokenize("a b")
    portunlp.spacy_tokenize("c d")
    assert calls["count"] == 1


def test_error_when_model_missing(monkeypatch):
    module = types.ModuleType("spacy")

    def load(name: str):
        raise OSError("model missing")

    module.load = load
    monkeypatch.setitem(sys.modules, "spacy", module)
    portunlp = importlib.reload(importlib.import_module("portunlp"))
    portunlp._nlp = None
    with pytest.raises(OSError):
        portunlp.spacy_tokenize("text")
