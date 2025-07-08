"""Python helpers for portuNLP.

This module provides minimal wrappers around spaCy for Portuguese NLP tasks.
"""
from __future__ import annotations

import spacy

_nlp = None

def _load_model() -> spacy.language.Language:
    """Load the spaCy Portuguese model lazily.

    Returns:
        spacy.language.Language: Loaded spaCy language model.
    """
    global _nlp
    if _nlp is None:
        try:
            _nlp = spacy.load("pt_core_news_sm")
        except OSError:
            raise OSError("spaCy Portuguese model not found. Run 'python -m spacy download pt_core_news_sm'.")
    return _nlp

def spacy_tokenize(text: str) -> list[str]:
    """Tokenize text using spaCy.

    Args:
        text (str): Text to tokenize.

    Returns:
        list[str]: List of token strings.
    """
    nlp = _load_model()
    doc = nlp(text)
    return [token.text for token in doc]

def spacy_lemmatize(text: str) -> list[str]:
    """Lemmatize text using spaCy.

    Args:
        text (str): Text to lemmatize.

    Returns:
        list[str]: List of lemma strings.
    """
    nlp = _load_model()
    doc = nlp(text)
    return [token.lemma_ for token in doc]


def spacy_pos_tag(text: str) -> list[str]:
    """Generate POS tags using spaCy.

    Args:
        text (str): Text to tag.

    Returns:
        list[str]: List of part-of-speech tags.
    """
    nlp = _load_model()
    doc = nlp(text)
    return [token.pos_ for token in doc]
