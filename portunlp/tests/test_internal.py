import importlib
import json
import types

import pytest


@pytest.fixture()
def fake_spacy(monkeypatch):
    """Provide a fake spaCy module for testing."""

    module = types.ModuleType("spacy")

    class DummyToken:
        def __init__(self, text: str, index: int) -> None:
            self.text = text
            self.i = index
            self.lemma_ = text.lower()
            self.pos_ = "NOUN"
            self.tag_ = "NOUN__Sing"
            self.dep_ = "ROOT" if index == 0 else "obj"
            self.is_alpha = text.isalpha()
            self.is_stop = text.lower() in {"a", "e"}
            self.morph = types.SimpleNamespace(
                to_dict=lambda: {"Number": "Sing"} if text.isalpha() else {}
            )
            self.head = self

    class DummySentence:
        def __init__(self, text: str, start: int, end: int, root: DummyToken) -> None:
            self.text = text
            self.start = start
            self.end = end
            self.root = root

    class DummyEntity:
        def __init__(self, text: str, label: str, start: int, end: int) -> None:
            self.text = text
            self.label_ = label
            self.start = start
            self.end = end

    class DummyNounChunk:
        def __init__(self, text: str, root: DummyToken, start: int, end: int) -> None:
            self.text = text
            self.root = root
            self.start = start
            self.end = end

    class DummyNLP:
        def __call__(self, text: str):
            normalized_text = text.replace("|", " ")
            tokens = [
                DummyToken(token_text, index)
                for index, token_text in enumerate(normalized_text.split())
            ]
            if tokens:
                root = tokens[0]
                for token in tokens[1:]:
                    token.head = root

            class DummyDoc(list):
                @property
                def ents(self):
                    entities = []
                    for index, token in enumerate(self):
                        if token.text[:1].isupper():
                            entities.append(DummyEntity(token.text, "PER", index, index + 1))
                    return entities

                @property
                def noun_chunks(self):
                    chunks = []
                    for index, token in enumerate(self):
                        if token.is_alpha:
                            chunks.append(DummyNounChunk(token.text, token, index, index + 1))
                    return chunks

                @property
                def sents(self):
                    sentences = []
                    start = 0
                    for segment in text.split("|"):
                        cleaned = segment.strip()
                        if not cleaned:
                            continue
                        token_count = len(cleaned.split())
                        end = start + token_count
                        if end > start:
                            sentences.append(DummySentence(cleaned, start, end, self[start]))
                        start = end
                    return sentences

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


def test_spacy_morphology_returns_structured_summary(fake_spacy):
    spacy_helpers, _ = fake_spacy
    summary = spacy_helpers.spacy_morphology("a Casa")

    assert [token.text for token in summary.tokens] == ["a", "Casa"]
    assert summary.tokens[1].tag == "NOUN__Sing"
    assert summary.tokens[1].morph == {"Number": "Sing"}
    assert summary.lemmas == ["a", "casa"]
    assert summary.pos_counts == {"NOUN": 2}
    assert summary.morph_counts == {"Number=Sing": 2}


def test_spacy_entities_returns_structured_summary(fake_spacy):
    spacy_helpers, _ = fake_spacy
    summary = spacy_helpers.spacy_entities("Ana Casa")

    assert [entity.text for entity in summary.entities] == ["Ana", "Casa"]
    assert summary.entities[0].label == "PER"
    assert summary.entities[0].start == 0
    assert summary.entities[1].end == 2
    assert summary.label_counts == {"PER": 2}


def test_spacy_dependencies_returns_structured_summary(fake_spacy):
    spacy_helpers, _ = fake_spacy
    summary = spacy_helpers.spacy_dependencies("Ana Casa")

    assert [token.text for token in summary.tokens] == ["Ana", "Casa"]
    assert summary.tokens[0].dep == "ROOT"
    assert summary.tokens[1].head == "Ana"
    assert summary.tokens[1].head_index == 0
    assert summary.root == "Ana"
    assert summary.dep_counts == {"ROOT": 1, "obj": 1}


def test_spacy_noun_chunks_returns_structured_summary(fake_spacy):
    spacy_helpers, _ = fake_spacy
    summary = spacy_helpers.spacy_noun_chunks("Ana Casa")

    assert [chunk.text for chunk in summary.chunks] == ["Ana", "Casa"]
    assert summary.chunks[0].root == "Ana"
    assert summary.chunks[1].start == 1
    assert summary.chunks[1].end == 2
    assert summary.root_counts == {"Ana": 1, "Casa": 1}


def test_spacy_sentences_returns_structured_summary(fake_spacy):
    spacy_helpers, _ = fake_spacy
    summary = spacy_helpers.spacy_sentences("Ana Casa|Porto")

    assert summary.sentence_count == 2
    assert summary.sentences[0].text == "Ana Casa"
    assert summary.sentences[0].root == "Ana"
    assert summary.sentences[0].token_count == 2
    assert [entity.text for entity in summary.sentences[0].entities] == ["Ana", "Casa"]
    assert summary.sentences[1].start == 2
    assert summary.sentences[1].end == 3


def test_spacy_document_returns_full_summary(fake_spacy):
    spacy_helpers, _ = fake_spacy
    summary = spacy_helpers.spacy_document("Ana Casa|Porto")

    assert summary.text == "Ana Casa|Porto"
    assert [token.text for token in summary.tokens] == ["Ana", "Casa", "Porto"]
    assert summary.morphology.pos_counts == {"NOUN": 3}
    assert summary.entities.label_counts == {"PER": 3}
    assert summary.dependencies.root == "Ana"
    assert summary.noun_chunks.root_counts == {"Ana": 1, "Casa": 1, "Porto": 1}
    assert summary.sentences.sentence_count == 2


def test_spacy_corpus_returns_aggregate_summary(fake_spacy):
    spacy_helpers, _ = fake_spacy
    summary = spacy_helpers.spacy_corpus(["Ana Casa", "Porto"])

    assert summary.document_count == 2
    assert summary.token_count == 3
    assert [document.text for document in summary.documents] == ["Ana Casa", "Porto"]
    assert summary.pos_counts == {"NOUN": 3}
    assert summary.entity_label_counts == {"PER": 3}
    assert summary.dependency_counts == {"ROOT": 2, "obj": 1}
    assert summary.noun_chunk_root_counts == {"Ana": 1, "Casa": 1, "Porto": 1}


def test_spacy_corpus_validates_input(fake_spacy):
    spacy_helpers, _ = fake_spacy

    with pytest.raises(TypeError, match="`texts` must be a list or tuple of strings"):
        spacy_helpers.spacy_corpus("Ana Casa")  # type: ignore[arg-type]

    with pytest.raises(TypeError, match="`texts` must contain only strings"):
        spacy_helpers.spacy_corpus(["Ana Casa", 1])  # type: ignore[list-item]


def test_spacy_to_dict_serializes_nested_summaries(fake_spacy):
    spacy_helpers, _ = fake_spacy
    summary = spacy_helpers.spacy_document("Ana Casa|Porto")
    payload = spacy_helpers.spacy_to_dict(summary)

    assert payload["text"] == "Ana Casa|Porto"
    assert payload["tokens"][0]["text"] == "Ana"
    assert payload["entities"]["label_counts"] == {"PER": 3}
    assert payload["sentences"]["sentence_count"] == 2


def test_spacy_to_json_serializes_nested_summaries(fake_spacy):
    spacy_helpers, _ = fake_spacy
    summary = spacy_helpers.spacy_corpus(["Ana Casa", "Porto"])
    payload = json.loads(spacy_helpers.spacy_to_json(summary, indent=None))

    assert payload["document_count"] == 2
    assert payload["documents"][0]["text"] == "Ana Casa"
    assert payload["dependency_counts"] == {"ROOT": 2, "obj": 1}


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
