"""Native Portuguese text-processing helpers."""

from __future__ import annotations

import re
import unicodedata
from pathlib import Path
from typing import Literal, Mapping

from ._data import ORTHOGRAPHIC_RULES, PORTUGUESE_STOPWORDS, POS_TAG_MAP, SLANG_MAP

_EMOJI_PATTERN = re.compile(
    "["
    "\U0001F300-\U0001F5FF"
    "\U0001F600-\U0001F64F"
    "\U0001F680-\U0001F6FF"
    "\U0001F700-\U0001F77F"
    "\U0001F780-\U0001F7FF"
    "\U0001F800-\U0001F8FF"
    "\U0001F900-\U0001F9FF"
    "\U0001FA00-\U0001FA6F"
    "\U0001FA70-\U0001FAFF"
    "\u2600-\u26FF"
    "\u2700-\u27BF"
    "]+",
    flags=re.UNICODE,
)
_WORD_BOUNDARY_TEMPLATE = r"(?<!\w){term}(?!\w)"


def _ensure_text(value: str, *, name: str = "text") -> str:
    """Validate a text argument.

    Args:
        value (str): Candidate text value.
        name (str): Parameter name for error messages.

    Returns:
        str: The validated input.

    Raises:
        TypeError: If the provided value is not a string.
    """
    if not isinstance(value, str):
        raise TypeError(f"`{name}` must be a string")
    return value


def _normalize_iterable(value: list[str] | tuple[str, ...] | set[str] | None, *, name: str) -> list[str]:
    """Validate and normalize an iterable of strings.

    Args:
        value (list[str] | tuple[str, ...] | set[str] | None): Candidate values.
        name (str): Parameter name for error messages.

    Returns:
        list[str]: Normalized string values.

    Raises:
        TypeError: If the provided iterable contains non-string values.
    """
    if value is None:
        return []

    normalized = list(value)
    if not all(isinstance(item, str) for item in normalized):
        raise TypeError(f"`{name}` must contain only strings")
    return normalized


def _iter_word_tokens(text: str) -> list[str]:
    """Split text into lowercase alphanumeric tokens.

    Args:
        text (str): Input text.

    Returns:
        list[str]: Extracted word tokens.
    """
    tokens: list[str] = []
    current: list[str] = []

    for character in text:
        if character.isalnum():
            current.append(character.lower())
            continue

        if current:
            tokens.append("".join(current))
            current.clear()

    if current:
        tokens.append("".join(current))

    return tokens


def _remove_unicode_punctuation(text: str) -> str:
    """Remove Unicode punctuation characters from text.

    Args:
        text (str): Input text.

    Returns:
        str: Text without punctuation characters.
    """
    return "".join(character for character in text if not unicodedata.category(character).startswith("P"))


def normalize_accents(text: str) -> str:
    """Fold accented characters to ASCII equivalents.

    Args:
        text (str): Input text.

    Returns:
        str: Accent-normalized text.
    """
    normalized = unicodedata.normalize("NFKD", _ensure_text(text))
    return "".join(character for character in normalized if not unicodedata.combining(character))


def remove_emoji(text: str) -> str:
    """Remove emoji characters from text.

    Args:
        text (str): Input text.

    Returns:
        str: Text without emoji characters.
    """
    return _EMOJI_PATTERN.sub("", _ensure_text(text))


def apply_orthographic_rules(
    text: str,
    rules: tuple[tuple[str, str], ...] | None = None,
) -> str:
    """Apply built-in orthographic replacement rules.

    Args:
        text (str): Input text.
        rules (tuple[tuple[str, str], ...] | None): Optional replacement rules.

    Returns:
        str: Text with orthographic replacements applied.
    """
    result = _ensure_text(text)
    for source, target in rules or ORTHOGRAPHIC_RULES:
        result = result.replace(source, target)
    return result


def normalize_text(
    text: str,
    *,
    lower: bool = True,
    remove_punct: bool = False,
    correct: bool = False,
) -> str:
    """Normalize Portuguese text.

    Args:
        text (str): Input text.
        lower (bool): Whether to lowercase the text.
        remove_punct (bool): Whether to remove punctuation.
        correct (bool): Whether to apply orthographic replacements.

    Returns:
        str: Normalized text.
    """
    result = _ensure_text(text)

    if lower:
        result = result.lower()
    if remove_punct:
        result = _remove_unicode_punctuation(result)
    if correct:
        result = apply_orthographic_rules(result)

    return normalize_accents(result)


def tokenize_text(text: str, *, kind: Literal["word", "sentence"] = "word") -> list[str]:
    """Tokenize Portuguese text with a lightweight native tokenizer.

    Args:
        text (str): Input text.
        kind (Literal["word", "sentence"]): Tokenization mode.

    Returns:
        list[str]: Extracted tokens or sentences.

    Raises:
        ValueError: If the tokenization mode is unsupported.
    """
    normalized_text = _ensure_text(text)
    if not normalized_text:
        return []

    if kind == "word":
        return _iter_word_tokens(normalized_text)
    if kind == "sentence":
        return [
            sentence.strip()
            for sentence in re.split(r"(?<=[.!?])\s+", normalized_text.strip())
            if sentence.strip()
        ]
    raise ValueError("`kind` must be either 'word' or 'sentence'")


def tokenize_pt(text: str, type: Literal["word", "sentence"] = "word") -> list[str]:
    """Tokenize Portuguese text using the legacy package API.

    Args:
        text (str): Input text.
        type (Literal["word", "sentence"]): Tokenization mode.

    Returns:
        list[str]: Extracted tokens or sentences.
    """
    return tokenize_text(text, kind=type)


def load_dictionary(path: str | Path) -> list[str]:
    """Load a newline-delimited dictionary file.

    Args:
        path (str | Path): Path to a text file with one entry per line.

    Returns:
        list[str]: Cleaned dictionary terms.

    Raises:
        FileNotFoundError: If the target file does not exist.
    """
    dictionary_path = Path(path)
    if not dictionary_path.exists():
        raise FileNotFoundError(f"File not found: {dictionary_path}")

    lines = dictionary_path.read_text(encoding="utf-8").splitlines()
    return [line.strip() for line in lines if line.strip()]


def load_dict(path: str | Path) -> list[str]:
    """Load a newline-delimited dictionary file using the legacy API.

    Args:
        path (str | Path): Path to a text file with one entry per line.

    Returns:
        list[str]: Cleaned dictionary terms.
    """
    return load_dictionary(path)


def map_slang(text: str, custom_map: Mapping[str, str] | None = None) -> str:
    """Replace slang terms with standard Portuguese forms.

    Args:
        text (str): Input text.
        custom_map (Mapping[str, str] | None): Optional additional replacements.

    Returns:
        str: Text with slang terms replaced.
    """
    result = _ensure_text(text)
    replacements = dict(SLANG_MAP)
    if custom_map is not None:
        if not all(isinstance(key, str) and isinstance(value, str) for key, value in custom_map.items()):
            raise TypeError("`custom_map` must map strings to strings")
        replacements.update(custom_map)

    for term, replacement in replacements.items():
        pattern = re.compile(_WORD_BOUNDARY_TEMPLATE.format(term=re.escape(term)), flags=re.IGNORECASE)
        result = pattern.sub(replacement, result)
    return result


def clean_social_text(
    text: str,
    *,
    emoji: bool = True,
    accents: bool = True,
    slang: bool = True,
    custom_map: Mapping[str, str] | None = None,
) -> str:
    """Clean Portuguese social-media text.

    Args:
        text (str): Input text.
        emoji (bool): Whether to remove emoji.
        accents (bool): Whether to fold accents to ASCII.
        slang (bool): Whether to replace slang terms.
        custom_map (Mapping[str, str] | None): Optional slang overrides.

    Returns:
        str: Cleaned text.
    """
    result = _ensure_text(text)
    if emoji:
        result = remove_emoji(result)
    if slang:
        result = map_slang(result, custom_map=custom_map)
    if accents:
        result = normalize_accents(result)
    return result


def clean_social(
    text: str,
    *,
    emoji: bool = True,
    accents: bool = True,
    slang: bool = True,
    custom_map: Mapping[str, str] | None = None,
) -> str:
    """Clean Portuguese social-media text using the legacy API.

    Args:
        text (str): Input text.
        emoji (bool): Whether to remove emoji.
        accents (bool): Whether to fold accents to ASCII.
        slang (bool): Whether to replace slang terms.
        custom_map (Mapping[str, str] | None): Optional slang overrides.

    Returns:
        str: Cleaned text.
    """
    return clean_social_text(
        text,
        emoji=emoji,
        accents=accents,
        slang=slang,
        custom_map=custom_map,
    )


def get_stopwords(
    *,
    extra: list[str] | tuple[str, ...] | set[str] | None = None,
    omit: list[str] | tuple[str, ...] | set[str] | None = None,
) -> list[str]:
    """Return built-in Portuguese stopwords with optional additions and removals.

    Args:
        extra (list[str] | tuple[str, ...] | set[str] | None): Extra stopwords to add.
        omit (list[str] | tuple[str, ...] | set[str] | None): Stopwords to remove.

    Returns:
        list[str]: The final stopword list.
    """
    words = list(PORTUGUESE_STOPWORDS)
    additions = _normalize_iterable(extra, name="extra")
    removals = set(_normalize_iterable(omit, name="omit"))

    seen: set[str] = set()
    ordered_words: list[str] = []
    for word in [*words, *additions]:
        if word not in removals and word not in seen:
            ordered_words.append(word)
            seen.add(word)
    return ordered_words


def map_pos_tags(tags: list[str] | tuple[str, ...]) -> list[str]:
    """Map spaCy POS tags to the package's universal tagset.

    Args:
        tags (list[str] | tuple[str, ...]): POS tags to map.

    Returns:
        list[str]: Mapped POS tags.
    """
    normalized_tags = _normalize_iterable(tags, name="tags")
    return [POS_TAG_MAP.get(tag, tag) for tag in normalized_tags]


def lemmatize_pt(text: str) -> list[str]:
    """Lemmatize Portuguese text using spaCy.

    Args:
        text (str): Input text.

    Returns:
        list[str]: Lemmas produced by spaCy.
    """
    from ._spacy import spacy_lemmatize

    return spacy_lemmatize(text)


def pos_tag_pt(text: str, *, universal: bool = False) -> list[str]:
    """Tag Portuguese text with spaCy and optionally map tags.

    Args:
        text (str): Input text.
        universal (bool): Whether to map tags through the bundled POS map.

    Returns:
        list[str]: POS tags.
    """
    from ._spacy import spacy_pos_tag

    tags = spacy_pos_tag(text)
    return map_pos_tags(tags) if universal else tags


def tokenize_spacy_pt(text: str) -> list[str]:
    """Tokenize Portuguese text with spaCy.

    Args:
        text (str): Input text.

    Returns:
        list[str]: Tokens produced by spaCy.
    """
    from ._spacy import spacy_tokenize

    return spacy_tokenize(text)


apply_orth_rules = apply_orthographic_rules
