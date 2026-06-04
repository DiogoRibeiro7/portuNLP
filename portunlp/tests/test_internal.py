import importlib
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
            self.is_alpha = text.isalpha()
            self.is_stop = text.lower() in {"a", "e"}

    class DummySentence:
        def __init__(self, text: str) -> None:
            self.text = text

    class DummyNLP:
        def __call__(self, text: str):
            tokens = [DummyToken(t) for t in text.split()]

            class DummyDoc(list):
                @property
                def sents(self):
                    return [DummySentence(sentence.strip()) for sentence in text.split("|") if sentence.strip()]

            return DummyDoc(tokens)

    calls = {"count": 0}

    def load(name: str):
        calls["count"] += 1
        return DummyNLP()

    module.load = load
    def fake_import_module(name: str) -> types.ModuleType:
        if name == "spacy":
            return module
        return importlib.import_module(name)

    spacy_helpers = importlib.reload(importlib.import_module("portunlp._spacy"))
    monkeypatch.setattr(spacy_helpers, "import_module", fake_import_module)
    spacy_helpers._nlp = None
    return spacy_helpers, calls


def test_load_model_caches(fake_spacy):
    spacy_helpers, calls = fake_spacy
    spacy_helpers.spacy_tokenize("a b")
    spacy_helpers.spacy_tokenize("c d")
    assert calls["count"] == 1


def test_spacy_sentencize_returns_sentences(fake_spacy):
    spacy_helpers, _ = fake_spacy
    assert spacy_helpers.spacy_sentencize("um|dois") == ["um", "dois"]


def test_spacy_analyze_returns_structured_tokens(fake_spacy):
    spacy_helpers, _ = fake_spacy
    tokens = spacy_helpers.spacy_analyze("a Casa")
    assert [token.text for token in tokens] == ["a", "Casa"]
    assert tokens[0].is_stop is True
    assert tokens[1].lemma == "casa"
    assert tokens[1].pos == "NOUN"


def test_error_when_model_missing(monkeypatch):
    spacy_helpers = importlib.reload(importlib.import_module("portunlp._spacy"))

    def fake_import_module(name: str) -> types.ModuleType:
        raise ModuleNotFoundError(name)

    monkeypatch.setattr(spacy_helpers, "import_module", fake_import_module)
    spacy_helpers._nlp = None

    with pytest.raises(OSError, match="spaCy is not installed"):
        spacy_helpers.spacy_tokenize("text")


def test_error_when_portuguese_model_missing(monkeypatch):
    module = types.ModuleType("spacy")

    def load(name: str):
        raise OSError("model missing")

    module.load = load

    def fake_import_module(name: str) -> types.ModuleType:
        if name == "spacy":
            return module
        return importlib.import_module(name)

    spacy_helpers = importlib.reload(importlib.import_module("portunlp._spacy"))
    monkeypatch.setattr(spacy_helpers, "import_module", fake_import_module)
    spacy_helpers._nlp = None

    with pytest.raises(OSError, match="pt_core_news_sm"):
        spacy_helpers.spacy_tokenize("text")


def test_import_without_spacy_dependency(monkeypatch):
    original_import_module = importlib.import_module

    def fake_import_module(name: str):
        if name == "spacy":
            raise ModuleNotFoundError(name)
        return original_import_module(name)

    monkeypatch.setattr(importlib, "import_module", fake_import_module)

    portunlp = importlib.reload(original_import_module("portunlp"))

    assert hasattr(portunlp, "spacy_tokenize")
    assert hasattr(portunlp, "spacy_analyze")
