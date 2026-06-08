"""High-level analysis facade for Portuguese NLP workflows."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from .text import (
    CorpusStatistics,
    KeywordScore,
    ProcessedText,
    TextStatistics,
    analyze_corpus,
    analyze_text_metrics,
    compute_inverse_document_frequency,
    extract_keywords,
    preprocess_text,
)


@dataclass(frozen=True)
class TextAnalysis:
    """Composed analysis result for a single text.

    Attributes:
        text (str): Original input text.
        processed (ProcessedText): Preprocessing pipeline output.
        metrics (TextStatistics): Descriptive text metrics.
        keywords (list[KeywordScore]): Ranked keyword scores.
        spacy_document (object | None): Optional structured spaCy document summary.
        spacy_lexicon (object | None): Optional spaCy lexical summary.
        spacy_collocations (object | None): Optional spaCy collocation summary.
    """

    text: str
    processed: ProcessedText
    metrics: TextStatistics
    keywords: list[KeywordScore]
    spacy_document: object | None
    spacy_lexicon: object | None
    spacy_collocations: object | None


@dataclass(frozen=True)
class CorpusAnalysis:
    """Composed analysis result for multiple texts.

    Attributes:
        texts (list[str]): Original input texts.
        processed_documents (list[ProcessedText]): Per-document preprocessing outputs.
        statistics (CorpusStatistics): Aggregate token and n-gram statistics.
        idf_values (dict[str, float]): Smoothed inverse document frequency values.
        spacy_corpus (object | None): Optional structured spaCy corpus summary.
        spacy_lexicon (object | None): Optional spaCy lexical corpus summary.
        spacy_collocations (object | None): Optional spaCy collocation corpus summary.
    """

    texts: list[str]
    processed_documents: list[ProcessedText]
    statistics: CorpusStatistics
    idf_values: dict[str, float]
    spacy_corpus: object | None
    spacy_lexicon: object | None
    spacy_collocations: object | None


def _ensure_texts(texts: list[str] | tuple[str, ...], *, name: str = "texts") -> list[str]:
    """Validate a sequence of text values.

    Args:
        texts (list[str] | tuple[str, ...]): Candidate text sequence.
        name (str): Parameter name for error messages.

    Returns:
        list[str]: Normalized text values.

    Raises:
        TypeError: If the sequence is invalid or contains non-string values.
    """
    if not isinstance(texts, (list, tuple)):
        raise TypeError(f"`{name}` must be a list or tuple of strings")
    normalized = list(texts)
    if not all(isinstance(text, str) for text in normalized):
        raise TypeError(f"`{name}` must contain only strings")
    return normalized


def analyze_text(
    text: str,
    *,
    correct: bool = False,
    remove_punct: bool = True,
    social: bool = False,
    custom_map: Mapping[str, str] | None = None,
    remove_stopwords: bool = False,
    use_spacy: bool = False,
    keyword_top_k: int = 10,
    include_spacy: bool = False,
    include_spacy_lexicon: bool = False,
    include_spacy_collocations: bool = False,
    collocation_size: int = 2,
) -> TextAnalysis:
    """Run a composed high-level analysis for one text.

    Args:
        text (str): Input text.
        correct (bool): Whether to apply orthographic corrections.
        remove_punct (bool): Whether to remove punctuation during normalization.
        social (bool): Whether to apply social-text cleaning before normalization.
        custom_map (Mapping[str, str] | None): Optional slang overrides.
        remove_stopwords (bool): Whether to remove stopwords from the token list.
        use_spacy (bool): Whether to use spaCy tokenization in text preprocessing.
        keyword_top_k (int): Maximum number of keywords to return.
        include_spacy (bool): Whether to include a structured spaCy document summary.
        include_spacy_lexicon (bool): Whether to include a spaCy lexical summary.
        include_spacy_collocations (bool): Whether to include a spaCy collocation summary.
        collocation_size (int): Size of collocations to extract when enabled.

    Returns:
        TextAnalysis: Composed text analysis result.
    """
    processed = preprocess_text(
        text,
        correct=correct,
        remove_punct=remove_punct,
        social=social,
        custom_map=custom_map,
        remove_stopwords=remove_stopwords,
        use_spacy=use_spacy,
    )
    metrics = analyze_text_metrics(
        text,
        correct=correct,
        remove_punct=remove_punct,
        social=social,
        custom_map=custom_map,
        remove_stopwords=remove_stopwords,
        use_spacy=use_spacy,
    )
    keywords = extract_keywords(
        text,
        top_k=keyword_top_k,
        correct=correct,
        remove_punct=remove_punct,
        social=social,
        custom_map=custom_map,
        remove_stopwords=remove_stopwords,
        use_spacy=use_spacy,
    )

    spacy_document = None
    spacy_lexicon = None
    spacy_collocations = None

    if include_spacy or include_spacy_lexicon or include_spacy_collocations:
        from . import _spacy

        if include_spacy:
            spacy_document = _spacy.spacy_document(text)
        if include_spacy_lexicon:
            spacy_lexicon = _spacy.spacy_lexicon(text)
        if include_spacy_collocations:
            spacy_collocations = _spacy.spacy_collocations(text, n=collocation_size)

    return TextAnalysis(
        text=text,
        processed=processed,
        metrics=metrics,
        keywords=keywords,
        spacy_document=spacy_document,
        spacy_lexicon=spacy_lexicon,
        spacy_collocations=spacy_collocations,
    )


def analyze_texts(
    texts: list[str] | tuple[str, ...],
    *,
    correct: bool = False,
    remove_punct: bool = True,
    social: bool = False,
    custom_map: Mapping[str, str] | None = None,
    remove_stopwords: bool = False,
    use_spacy: bool = False,
    ngram_size: int = 2,
    include_spacy: bool = False,
    include_spacy_lexicon: bool = False,
    include_spacy_collocations: bool = False,
    collocation_size: int = 2,
) -> CorpusAnalysis:
    """Run a composed high-level analysis for multiple texts.

    Args:
        texts (list[str] | tuple[str, ...]): Input texts.
        correct (bool): Whether to apply orthographic corrections.
        remove_punct (bool): Whether to remove punctuation during normalization.
        social (bool): Whether to apply social-text cleaning before normalization.
        custom_map (Mapping[str, str] | None): Optional slang overrides.
        remove_stopwords (bool): Whether to remove stopwords from token lists.
        use_spacy (bool): Whether to use spaCy tokenization in text preprocessing.
        ngram_size (int): Size of n-grams for aggregate statistics.
        include_spacy (bool): Whether to include a structured spaCy corpus summary.
        include_spacy_lexicon (bool): Whether to include a spaCy lexical corpus summary.
        include_spacy_collocations (bool): Whether to include a spaCy collocation corpus summary.
        collocation_size (int): Size of collocations to extract when enabled.

    Returns:
        CorpusAnalysis: Composed corpus analysis result.
    """
    normalized_texts = _ensure_texts(texts)
    processed_documents = [
        preprocess_text(
            text,
            correct=correct,
            remove_punct=remove_punct,
            social=social,
            custom_map=custom_map,
            remove_stopwords=remove_stopwords,
            use_spacy=use_spacy,
        )
        for text in normalized_texts
    ]
    statistics = analyze_corpus(
        normalized_texts,
        correct=correct,
        remove_punct=remove_punct,
        social=social,
        custom_map=custom_map,
        remove_stopwords=remove_stopwords,
        use_spacy=use_spacy,
        ngram_size=ngram_size,
    )
    idf_values = compute_inverse_document_frequency(
        normalized_texts,
        correct=correct,
        remove_punct=remove_punct,
        social=social,
        custom_map=custom_map,
        remove_stopwords=remove_stopwords,
        use_spacy=use_spacy,
    )

    spacy_corpus = None
    spacy_lexicon = None
    spacy_collocations = None

    if include_spacy or include_spacy_lexicon or include_spacy_collocations:
        from . import _spacy

        if include_spacy:
            spacy_corpus = _spacy.spacy_corpus(normalized_texts)
        if include_spacy_lexicon:
            spacy_lexicon = _spacy.spacy_lexicon_corpus(normalized_texts)
        if include_spacy_collocations:
            spacy_collocations = _spacy.spacy_collocations_corpus(
                normalized_texts,
                n=collocation_size,
            )

    return CorpusAnalysis(
        texts=normalized_texts,
        processed_documents=processed_documents,
        statistics=statistics,
        idf_values=idf_values,
        spacy_corpus=spacy_corpus,
        spacy_lexicon=spacy_lexicon,
        spacy_collocations=spacy_collocations,
    )
