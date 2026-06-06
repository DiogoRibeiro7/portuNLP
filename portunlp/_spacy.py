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
