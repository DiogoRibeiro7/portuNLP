"""spaCy-backed helpers for Portuguese NLP tasks."""

from __future__ import annotations

from dataclasses import dataclass
from importlib import import_module
from typing import TYPE_CHECKING, Any, cast

if TYPE_CHECKING:
    from spacy.language import Language
else:
    Language = Any

SPACY_MODEL_NAME = "pt_core_news_sm"

_nlp: Language | None = None


@dataclass(frozen=True)
class SpacyToken:
    """Structured token information extracted from spaCy.

    Attributes:
        text (str): Original token text.
        lemma (str): Lemmatized token form.
        pos (str): spaCy POS tag.
        is_alpha (bool): Whether the token contains only alphabetic characters.
        is_stop (bool): Whether spaCy marks the token as a stopword.
    """

    text: str
    lemma: str
    pos: str
    is_alpha: bool
    is_stop: bool


@dataclass(frozen=True)
class SpacyMorphToken:
    """Structured token information with morphological features.

    Attributes:
        text (str): Original token text.
        lemma (str): Lemmatized token form.
        pos (str): spaCy POS tag.
        tag (str): spaCy fine-grained tag.
        morph (dict[str, str]): Morphological features emitted by spaCy.
        is_alpha (bool): Whether the token contains only alphabetic characters.
        is_stop (bool): Whether spaCy marks the token as a stopword.
    """

    text: str
    lemma: str
    pos: str
    tag: str
    morph: dict[str, str]
    is_alpha: bool
    is_stop: bool


@dataclass(frozen=True)
class SpacyMorphology:
    """Aggregate morphology summary extracted by spaCy.

    Attributes:
        tokens (list[SpacyMorphToken]): Structured token information.
        lemmas (list[str]): Lemmas for alphabetic tokens.
        pos_counts (dict[str, int]): Frequency of POS tags.
        morph_counts (dict[str, int]): Frequency of morphological feature pairs.
    """

    tokens: list[SpacyMorphToken]
    lemmas: list[str]
    pos_counts: dict[str, int]
    morph_counts: dict[str, int]


@dataclass(frozen=True)
class SpacyEntity:
    """Structured named entity extracted by spaCy.

    Attributes:
        text (str): Entity surface form.
        label (str): spaCy entity label.
        start (int): Start token index.
        end (int): End token index, exclusive.
    """

    text: str
    label: str
    start: int
    end: int


@dataclass(frozen=True)
class SpacyEntities:
    """Aggregate named-entity summary extracted by spaCy.

    Attributes:
        entities (list[SpacyEntity]): Structured named entities.
        label_counts (dict[str, int]): Frequency of entity labels.
    """

    entities: list[SpacyEntity]
    label_counts: dict[str, int]


@dataclass(frozen=True)
class SpacyDependencyToken:
    """Structured dependency information for a spaCy token.

    Attributes:
        text (str): Token surface form.
        dep (str): Dependency label.
        head (str): Surface form of the token head.
        head_index (int): Token index of the head.
        index (int): Token index in the document.
        pos (str): spaCy POS tag.
    """

    text: str
    dep: str
    head: str
    head_index: int
    index: int
    pos: str


@dataclass(frozen=True)
class SpacyDependencies:
    """Aggregate dependency summary extracted by spaCy.

    Attributes:
        tokens (list[SpacyDependencyToken]): Structured dependency tokens.
        root (str): Root token text, if available.
        dep_counts (dict[str, int]): Frequency of dependency labels.
    """

    tokens: list[SpacyDependencyToken]
    root: str
    dep_counts: dict[str, int]


@dataclass(frozen=True)
class SpacyNounChunk:
    """Structured noun chunk extracted by spaCy.

    Attributes:
        text (str): Chunk surface form.
        root (str): Root token of the chunk.
        start (int): Start token index.
        end (int): End token index, exclusive.
    """

    text: str
    root: str
    start: int
    end: int


@dataclass(frozen=True)
class SpacyNounChunks:
    """Aggregate noun-chunk summary extracted by spaCy.

    Attributes:
        chunks (list[SpacyNounChunk]): Structured noun chunks.
        root_counts (dict[str, int]): Frequency of noun-chunk roots.
    """

    chunks: list[SpacyNounChunk]
    root_counts: dict[str, int]


@dataclass(frozen=True)
class SpacySentence:
    """Structured sentence summary extracted by spaCy.

    Attributes:
        text (str): Sentence text.
        start (int): Start token index.
        end (int): End token index, exclusive.
        root (str): Root token text for the sentence.
        token_count (int): Number of tokens in the sentence.
        entities (list[SpacyEntity]): Named entities that belong to the sentence.
    """

    text: str
    start: int
    end: int
    root: str
    token_count: int
    entities: list[SpacyEntity]


@dataclass(frozen=True)
class SpacySentences:
    """Aggregate sentence summary extracted by spaCy.

    Attributes:
        sentences (list[SpacySentence]): Structured sentence summaries.
        sentence_count (int): Number of detected sentences.
    """

    sentences: list[SpacySentence]
    sentence_count: int


@dataclass(frozen=True)
class SpacyDocument:
    """Structured document summary extracted by spaCy.

    Attributes:
        text (str): Original input text.
        tokens (list[SpacyToken]): Structured token metadata.
        morphology (SpacyMorphology): Morphology summary.
        entities (SpacyEntities): Named-entity summary.
        dependencies (SpacyDependencies): Dependency summary.
        noun_chunks (SpacyNounChunks): Noun-chunk summary.
        sentences (SpacySentences): Sentence summary.
    """

    text: str
    tokens: list[SpacyToken]
    morphology: SpacyMorphology
    entities: SpacyEntities
    dependencies: SpacyDependencies
    noun_chunks: SpacyNounChunks
    sentences: SpacySentences


@dataclass(frozen=True)
class SpacyCorpus:
    """Structured corpus summary extracted by spaCy.

    Attributes:
        documents (list[SpacyDocument]): Per-document structured analyses.
        document_count (int): Number of analyzed documents.
        token_count (int): Total number of tokens across documents.
        pos_counts (dict[str, int]): Aggregate POS counts across the corpus.
        entity_label_counts (dict[str, int]): Aggregate entity-label counts.
        dependency_counts (dict[str, int]): Aggregate dependency-label counts.
        noun_chunk_root_counts (dict[str, int]): Aggregate noun-chunk root counts.
    """

    documents: list[SpacyDocument]
    document_count: int
    token_count: int
    pos_counts: dict[str, int]
    entity_label_counts: dict[str, int]
    dependency_counts: dict[str, int]
    noun_chunk_root_counts: dict[str, int]


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


def _get_doc(text: str) -> Any:
    """Process text with spaCy and return the document object.

    Args:
        text (str): Text to process.

    Returns:
        Any: The processed spaCy document.

    Raises:
        OSError: If spaCy or the Portuguese model is not installed.
    """
    if not text:
        return None

    return _load_model()(text)


def _ensure_texts(texts: list[str] | tuple[str, ...], *, name: str = "texts") -> list[str]:
    """Validate a sequence of text inputs.

    Args:
        texts (list[str] | tuple[str, ...]): Candidate text sequence.
        name (str): Parameter name for error messages.

    Returns:
        list[str]: Validated text values.

    Raises:
        TypeError: If the sequence is invalid or contains non-string values.
    """
    if not isinstance(texts, (list, tuple)):
        raise TypeError(f"`{name}` must be a list or tuple of strings")
    if not all(isinstance(text, str) for text in texts):
        raise TypeError(f"`{name}` must contain only strings")
    return list(texts)


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
    doc = _get_doc(text)
    if doc is None:
        return []

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


def spacy_sentencize(text: str) -> list[str]:
    """Segment text into sentences using spaCy.

    Args:
        text (str): Text to segment.

    Returns:
        list[str]: Sentence strings emitted by spaCy.

    Raises:
        OSError: If spaCy or the Portuguese model is not installed.
    """
    doc = _get_doc(text)
    if doc is None:
        return []

    return [sentence.text for sentence in doc.sents]


def spacy_analyze(text: str) -> list[SpacyToken]:
    """Return structured token information extracted by spaCy.

    Args:
        text (str): Text to analyze.

    Returns:
        list[SpacyToken]: Structured token metadata.

    Raises:
        OSError: If spaCy or the Portuguese model is not installed.
    """
    doc = _get_doc(text)
    if doc is None:
        return []

    return [
        SpacyToken(
            text=token.text,
            lemma=token.lemma_,
            pos=token.pos_,
            is_alpha=token.is_alpha,
            is_stop=token.is_stop,
        )
        for token in doc
    ]


def spacy_morphology(text: str) -> SpacyMorphology:
    """Return token-level morphology and aggregate grammatical counts.

    Args:
        text (str): Text to analyze.

    Returns:
        SpacyMorphology: Structured morphology summary.

    Raises:
        OSError: If spaCy or the Portuguese model is not installed.
    """
    doc = _get_doc(text)
    if doc is None:
        return SpacyMorphology(tokens=[], lemmas=[], pos_counts={}, morph_counts={})

    tokens: list[SpacyMorphToken] = []
    pos_counts: dict[str, int] = {}
    morph_counts: dict[str, int] = {}

    for token in doc:
        morph = dict(token.morph.to_dict())
        tokens.append(
            SpacyMorphToken(
                text=token.text,
                lemma=token.lemma_,
                pos=token.pos_,
                tag=token.tag_,
                morph=morph,
                is_alpha=token.is_alpha,
                is_stop=token.is_stop,
            )
        )

        pos_counts[token.pos_] = pos_counts.get(token.pos_, 0) + 1
        for feature_name, feature_value in morph.items():
            key = f"{feature_name}={feature_value}"
            morph_counts[key] = morph_counts.get(key, 0) + 1

    lemmas = [token.lemma for token in tokens if token.is_alpha]
    return SpacyMorphology(
        tokens=tokens,
        lemmas=lemmas,
        pos_counts=pos_counts,
        morph_counts=morph_counts,
    )


def spacy_entities(text: str) -> SpacyEntities:
    """Return named entities and aggregate label counts.

    Args:
        text (str): Text to analyze.

    Returns:
        SpacyEntities: Structured named-entity summary.

    Raises:
        OSError: If spaCy or the Portuguese model is not installed.
    """
    doc = _get_doc(text)
    if doc is None:
        return SpacyEntities(entities=[], label_counts={})

    entities = [
        SpacyEntity(
            text=entity.text,
            label=entity.label_,
            start=entity.start,
            end=entity.end,
        )
        for entity in doc.ents
    ]

    label_counts: dict[str, int] = {}
    for entity in entities:
        label_counts[entity.label] = label_counts.get(entity.label, 0) + 1

    return SpacyEntities(entities=entities, label_counts=label_counts)


def spacy_dependencies(text: str) -> SpacyDependencies:
    """Return dependency relations and aggregate label counts.

    Args:
        text (str): Text to analyze.

    Returns:
        SpacyDependencies: Structured dependency summary.

    Raises:
        OSError: If spaCy or the Portuguese model is not installed.
    """
    doc = _get_doc(text)
    if doc is None:
        return SpacyDependencies(tokens=[], root="", dep_counts={})

    tokens = [
        SpacyDependencyToken(
            text=token.text,
            dep=token.dep_,
            head=token.head.text,
            head_index=token.head.i,
            index=token.i,
            pos=token.pos_,
        )
        for token in doc
    ]

    dep_counts: dict[str, int] = {}
    root = ""
    for token in tokens:
        dep_counts[token.dep] = dep_counts.get(token.dep, 0) + 1
        if token.dep == "ROOT" and not root:
            root = token.text

    return SpacyDependencies(tokens=tokens, root=root, dep_counts=dep_counts)


def spacy_noun_chunks(text: str) -> SpacyNounChunks:
    """Return noun chunks and aggregate root counts.

    Args:
        text (str): Text to analyze.

    Returns:
        SpacyNounChunks: Structured noun-chunk summary.

    Raises:
        OSError: If spaCy or the Portuguese model is not installed.
    """
    doc = _get_doc(text)
    if doc is None:
        return SpacyNounChunks(chunks=[], root_counts={})

    chunks = [
        SpacyNounChunk(
            text=chunk.text,
            root=chunk.root.text,
            start=chunk.start,
            end=chunk.end,
        )
        for chunk in doc.noun_chunks
    ]

    root_counts: dict[str, int] = {}
    for chunk in chunks:
        root_counts[chunk.root] = root_counts.get(chunk.root, 0) + 1

    return SpacyNounChunks(chunks=chunks, root_counts=root_counts)


def spacy_sentences(text: str) -> SpacySentences:
    """Return sentence-level summaries with roots and entities.

    Args:
        text (str): Text to analyze.

    Returns:
        SpacySentences: Structured sentence summaries.

    Raises:
        OSError: If spaCy or the Portuguese model is not installed.
    """
    doc = _get_doc(text)
    if doc is None:
        return SpacySentences(sentences=[], sentence_count=0)

    entities = [
        SpacyEntity(
            text=entity.text,
            label=entity.label_,
            start=entity.start,
            end=entity.end,
        )
        for entity in doc.ents
    ]

    sentences = [
        SpacySentence(
            text=sentence.text,
            start=sentence.start,
            end=sentence.end,
            root=sentence.root.text,
            token_count=sentence.end - sentence.start,
            entities=[
                entity
                for entity in entities
                if entity.start >= sentence.start and entity.end <= sentence.end
            ],
        )
        for sentence in doc.sents
    ]
    return SpacySentences(sentences=sentences, sentence_count=len(sentences))


def spacy_document(text: str) -> SpacyDocument:
    """Return a full structured document summary extracted by spaCy.

    Args:
        text (str): Text to analyze.

    Returns:
        SpacyDocument: Full structured document analysis.

    Raises:
        OSError: If spaCy or the Portuguese model is not installed.
    """
    analyzed_text = text
    return SpacyDocument(
        text=analyzed_text,
        tokens=spacy_analyze(analyzed_text),
        morphology=spacy_morphology(analyzed_text),
        entities=spacy_entities(analyzed_text),
        dependencies=spacy_dependencies(analyzed_text),
        noun_chunks=spacy_noun_chunks(analyzed_text),
        sentences=spacy_sentences(analyzed_text),
    )


def spacy_corpus(texts: list[str] | tuple[str, ...]) -> SpacyCorpus:
    """Return a structured corpus summary extracted by spaCy.

    Args:
        texts (list[str] | tuple[str, ...]): Texts to analyze.

    Returns:
        SpacyCorpus: Structured corpus analysis.

    Raises:
        OSError: If spaCy or the Portuguese model is not installed.
        TypeError: If the input is not a sequence of strings.
    """
    normalized_texts = _ensure_texts(texts)
    documents = [spacy_document(text) for text in normalized_texts]

    pos_counts: dict[str, int] = {}
    entity_label_counts: dict[str, int] = {}
    dependency_counts: dict[str, int] = {}
    noun_chunk_root_counts: dict[str, int] = {}

    for document in documents:
        for label, count in document.morphology.pos_counts.items():
            pos_counts[label] = pos_counts.get(label, 0) + count
        for label, count in document.entities.label_counts.items():
            entity_label_counts[label] = entity_label_counts.get(label, 0) + count
        for label, count in document.dependencies.dep_counts.items():
            dependency_counts[label] = dependency_counts.get(label, 0) + count
        for root, count in document.noun_chunks.root_counts.items():
            noun_chunk_root_counts[root] = noun_chunk_root_counts.get(root, 0) + count

    return SpacyCorpus(
        documents=documents,
        document_count=len(documents),
        token_count=sum(len(document.tokens) for document in documents),
        pos_counts=pos_counts,
        entity_label_counts=entity_label_counts,
        dependency_counts=dependency_counts,
        noun_chunk_root_counts=noun_chunk_root_counts,
    )
