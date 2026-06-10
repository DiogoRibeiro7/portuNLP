"""Native Portuguese text-processing helpers."""

from __future__ import annotations

from dataclasses import dataclass
from collections import Counter
import importlib.util
import math
from importlib import import_module
import os
import re
import site
import unicodedata
from pathlib import Path
import sys
from typing import Literal, Mapping

from ._data import (
    ORTHOGRAPHIC_RULES,
    PORTUGUESE_CONTRACTIONS,
    PORTUGUESE_SENTIMENT_LEXICON,
    PORTUGUESE_STOPWORDS,
    POS_TAG_MAP,
    SENTIMENT_INTENSIFIERS,
    SENTIMENT_NEGATIONS,
    SLANG_MAP,
    VARIANT_SPELLINGS,
)
from ._stemmer import snowball_stem

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


def _candidate_cpp_module_paths() -> list[Path]:
    """Collect likely locations for the compiled C++ extension.

    Returns:
        list[Path]: Candidate module paths.
    """
    package_dir = Path(__file__).resolve().parent
    candidates: list[Path] = []
    candidates.extend(package_dir.glob("_portunlp_cpp*.pyd"))
    candidates.extend(package_dir.parent.glob("build/**/_portunlp_cpp*.pyd"))
    candidates.extend(package_dir.parent.glob("dist/**/_portunlp_cpp*.pyd"))

    site_directories = []
    if hasattr(site, "getsitepackages"):
        site_directories.extend(site.getsitepackages())
    user_site = site.getusersitepackages()
    if user_site:
        site_directories.append(user_site)

    for directory in site_directories:
        candidates.extend(Path(directory).glob("portunlp/_portunlp_cpp*.pyd"))

    return [candidate for candidate in candidates if candidate.exists()]


def _extra_dll_directories() -> list[Path]:
    """Collect optional Windows DLL search directories.

    The compiled extension may depend on runtime DLLs (for example a MinGW
    runtime) that live outside the package directory. Locations can be supplied
    via the ``PORTUNLP_DLL_DIRECTORIES`` environment variable using the
    platform path separator.

    Returns:
        list[Path]: Existing directories to register before loading the backend.
    """
    raw = os.environ.get("PORTUNLP_DLL_DIRECTORIES", "")
    directories = [Path(part) for part in raw.split(os.pathsep) if part.strip()]
    return [directory for directory in directories if directory.exists()]


def _load_cpp_backend():
    """Load the compiled C++ backend when available.

    The backend is an optional acceleration layer. Any failure to import or
    load it (missing module, ABI mismatch, missing runtime DLL) is treated as
    "unavailable" so the package falls back to the pure-Python implementation
    instead of failing to import.

    Returns:
        object | None: The compiled backend module, or ``None`` if unavailable.
    """
    try:
        return import_module("portunlp._portunlp_cpp")
    except (ImportError, OSError):
        pass

    extra_dll_directories = _extra_dll_directories() if os.name == "nt" else []

    for candidate in _candidate_cpp_module_paths():
        try:
            if os.name == "nt":
                for directory in [candidate.parent, *extra_dll_directories]:
                    os.add_dll_directory(str(directory))

            spec = importlib.util.spec_from_file_location("portunlp._portunlp_cpp", candidate)
            if spec is None or spec.loader is None:
                continue

            module = importlib.util.module_from_spec(spec)
            sys.modules["portunlp._portunlp_cpp"] = module
            try:
                spec.loader.exec_module(module)
            except BaseException:
                # Avoid leaving a half-initialized module behind on failure.
                sys.modules.pop("portunlp._portunlp_cpp", None)
                raise
            return module
        except (ImportError, OSError):
            continue

    return None


_CPP_BACKEND = _load_cpp_backend()


@dataclass(frozen=True)
class ProcessedText:
    """Structured result of the text preprocessing pipeline.

    Attributes:
        original_text (str): Original input text.
        normalized_text (str): Final normalized text used for tokenization.
        sentences (list[str]): Sentence segmentation result.
        tokens (list[str]): Tokenization result.
        filtered_tokens (list[str]): Tokens after optional stopword removal.
    """

    original_text: str
    normalized_text: str
    sentences: list[str]
    tokens: list[str]
    filtered_tokens: list[str]


@dataclass(frozen=True)
class CorpusStatistics:
    """Aggregate statistics for a collection of Portuguese texts.

    Attributes:
        document_count (int): Number of processed documents.
        token_count (int): Total number of retained tokens.
        unique_token_count (int): Number of unique retained tokens.
        frequencies (dict[str, int]): Token frequency mapping.
        ngrams (dict[tuple[str, ...], int]): N-gram frequency mapping.
    """

    document_count: int
    token_count: int
    unique_token_count: int
    frequencies: dict[str, int]
    ngrams: dict[tuple[str, ...], int]


@dataclass(frozen=True)
class KeywordScore:
    """Weighted keyword score for a token.

    Attributes:
        token (str): Token string.
        score (float): TF-IDF-style score.
    """

    token: str
    score: float


@dataclass(frozen=True)
class SimilarityScore:
    """Similarity score for a ranked document match.

    Attributes:
        index (int): Original position of the matched document.
        text (str): Original matched document.
        score (float): Cosine similarity score.
    """

    index: int
    text: str
    score: float


@dataclass(frozen=True)
class TextStatistics:
    """Descriptive statistics for a single Portuguese text.

    Attributes:
        sentence_count (int): Number of detected sentences.
        token_count (int): Number of analyzed tokens.
        unique_token_count (int): Number of unique analyzed tokens.
        character_count (int): Character count of the normalized text.
        average_token_length (float): Mean token length in characters.
        average_sentence_length (float): Mean sentence length in tokens.
        lexical_diversity (float): Ratio of unique tokens to total tokens.
        syllable_count (int): Estimated total syllable count.
        average_syllables_per_word (float): Mean syllables per token.
        flesch_reading_ease (float): Readability estimate based on Flesch-style scoring.
    """

    sentence_count: int
    token_count: int
    unique_token_count: int
    character_count: int
    average_token_length: float
    average_sentence_length: float
    lexical_diversity: float
    syllable_count: int
    average_syllables_per_word: float
    flesch_reading_ease: float


@dataclass(frozen=True)
class SentimentScore:
    """Lexicon-based sentiment result for a text.

    Attributes:
        polarity (float): Mean polarity of scored words, in [-1.0, 1.0].
        label (str): "positive", "negative", or "neutral".
        positive_tokens (int): Number of tokens with a positive contribution.
        negative_tokens (int): Number of tokens with a negative contribution.
        token_count (int): Total number of tokens analyzed.
    """

    polarity: float
    label: str
    positive_tokens: int
    negative_tokens: int
    token_count: int


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


def _ensure_texts(value: list[str] | tuple[str, ...], *, name: str = "texts") -> list[str]:
    """Validate a sequence of texts.

    Args:
        value (list[str] | tuple[str, ...]): Candidate text sequence.
        name (str): Parameter name for error messages.

    Returns:
        list[str]: Normalized text sequence.

    Raises:
        TypeError: If the sequence is invalid or contains non-string values.
    """
    if not isinstance(value, (list, tuple)):
        raise TypeError(f"`{name}` must be a list or tuple of strings")
    return _normalize_iterable(value, name=name)


def cpp_acceleration_available() -> bool:
    """Report whether the optional compiled C++ backend is loaded.

    The backend accelerates tokenization, frequency counting, and n-gram
    generation. When it is unavailable the package transparently uses the
    pure-Python implementations, which produce identical results.

    Returns:
        bool: True if the compiled backend is loaded and in use.
    """
    return _CPP_BACKEND is not None


def _can_use_cpp_text(value: str) -> bool:
    """Check whether text is handled identically by the C++ tokenizer.

    The native tokenizer mirrors Python's ``str.isalnum()`` / ``str.lower()``
    only over ASCII and the Latin-1 Supplement letters (which cover Portuguese
    accented characters). Text containing any other non-ASCII code point falls
    back to the pure-Python tokenizer to guarantee identical output.

    Args:
        value (str): Input text.

    Returns:
        bool: Whether the C++ backend should be used for this text.
    """
    return all(ord(character) < 0x80 or 0x00C0 <= ord(character) <= 0x00FF for character in value)


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


def _count_syllables(token: str) -> int:
    """Estimate the number of syllables in a Portuguese token.

    Args:
        token (str): Input token.

    Returns:
        int: Estimated syllable count.
    """
    normalized = normalize_accents(token).lower()
    letters_only = "".join(character for character in normalized if character.isalpha())
    if not letters_only:
        return 0

    vowel_groups = re.findall(r"[aeiouy]+", letters_only)
    return max(1, len(vowel_groups))


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
        if _CPP_BACKEND is not None and _can_use_cpp_text(normalized_text):
            return list(_CPP_BACKEND.split_words(normalized_text))
        return _iter_word_tokens(normalized_text)
    if kind == "sentence":
        return [
            sentence.strip()
            for sentence in re.split(r"(?<=[.!?])\s+", normalized_text.strip())
            if sentence.strip()
        ]
    raise ValueError("`kind` must be either 'word' or 'sentence'")


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


def expand_contractions(text: str, custom_map: Mapping[str, str] | None = None) -> str:
    """Expand Portuguese preposition contractions into their components.

    Replaces whole-word contractions such as ``do`` -> ``de o``,
    ``na`` -> ``em a``, ``pelos`` -> ``por os``, and ``àquele`` -> ``a aquele``.
    Matching is case-insensitive and the expansion is emitted in lower case,
    which suits downstream normalization. Longer contractions are applied first
    so that, for example, ``daquele`` is not partially matched.

    Args:
        text (str): Input text.
        custom_map (Mapping[str, str] | None): Optional additional or overriding
            contraction-to-expansion mappings.

    Returns:
        str: Text with contractions expanded.

    Raises:
        TypeError: If ``custom_map`` contains non-string keys or values.
    """
    result = _ensure_text(text)
    replacements = dict(PORTUGUESE_CONTRACTIONS)
    if custom_map is not None:
        if not all(isinstance(key, str) and isinstance(value, str) for key, value in custom_map.items()):
            raise TypeError("`custom_map` must map strings to strings")
        replacements.update(custom_map)

    for term in sorted(replacements, key=len, reverse=True):
        pattern = re.compile(_WORD_BOUNDARY_TEMPLATE.format(term=re.escape(term)), flags=re.IGNORECASE)
        result = pattern.sub(replacements[term], result)
    return result


def _match_case(matched: str, replacement: str) -> str:
    """Apply the capitalization pattern of ``matched`` to ``replacement``.

    Args:
        matched (str): The originally matched text.
        replacement (str): The lower-case replacement.

    Returns:
        str: The replacement with matching capitalization.
    """
    if matched.isupper():
        return replacement.upper()
    if matched[:1].isupper():
        return replacement[:1].upper() + replacement[1:]
    return replacement


def convert_variant(text: str, *, to: str = "br") -> str:
    """Convert orthography between European and Brazilian Portuguese.

    Applies the bundled :data:`VARIANT_SPELLINGS` mapping for known orthographic
    differences (for example ``facto``/``fato`` and ``económico``/``econômico``).
    Matching is case-insensitive and capitalization is preserved. This is an
    orthographic conversion only; it does not handle lexical differences such as
    ``comboio``/``trem``.

    Args:
        text (str): Input text.
        to (str): Target variant: ``"br"`` (Brazilian) or ``"pt"``/``"eu"``
            (European).

    Returns:
        str: Text converted to the target variant.

    Raises:
        ValueError: If ``to`` is not a recognized variant.
    """
    result = _ensure_text(text)
    target = to.lower()
    if target in ("br", "brazilian", "pt-br"):
        source_index, target_index = 0, 1
    elif target in ("pt", "eu", "european", "pt-pt"):
        source_index, target_index = 1, 0
    else:
        raise ValueError("`to` must be one of 'br', 'pt', or 'eu'")

    for pair in VARIANT_SPELLINGS:
        source, destination = pair[source_index], pair[target_index]
        pattern = re.compile(_WORD_BOUNDARY_TEMPLATE.format(term=re.escape(source)), flags=re.IGNORECASE)

        def _replace(match: "re.Match[str]", dest: str = destination) -> str:
            return _match_case(match.group(0), dest)

        result = pattern.sub(_replace, result)
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


def filter_stopwords(
    tokens: list[str] | tuple[str, ...],
    *,
    stopwords: list[str] | tuple[str, ...] | set[str] | None = None,
    normalize: bool = False,
) -> list[str]:
    """Remove stopwords from a token sequence.

    Args:
        tokens (list[str] | tuple[str, ...]): Tokens to filter.
        stopwords (list[str] | tuple[str, ...] | set[str] | None): Optional stopword set.
        normalize (bool): Whether to accent-fold and lowercase before comparison.

    Returns:
        list[str]: Tokens that are not stopwords.
    """
    normalized_tokens = _normalize_iterable(tokens, name="tokens")
    configured_stopwords = get_stopwords() if stopwords is None else _normalize_iterable(stopwords, name="stopwords")
    stopword_set = set(configured_stopwords)

    if not normalize:
        return [token for token in normalized_tokens if token not in stopword_set]

    normalized_stopwords = {normalize_text(word, lower=True, remove_punct=False, correct=False) for word in stopword_set}
    return [
        token
        for token in normalized_tokens
        if normalize_text(token, lower=True, remove_punct=False, correct=False) not in normalized_stopwords
    ]


def generate_ngrams(tokens: list[str] | tuple[str, ...], n: int) -> list[tuple[str, ...]]:
    """Generate contiguous n-grams from a token sequence.

    Args:
        tokens (list[str] | tuple[str, ...]): Source token sequence.
        n (int): N-gram size.

    Returns:
        list[tuple[str, ...]]: Contiguous n-grams.

    Raises:
        ValueError: If `n` is smaller than 1.
    """
    normalized_tokens = _normalize_iterable(tokens, name="tokens")
    if n < 1:
        raise ValueError("`n` must be at least 1")
    # N-gram generation stays in pure Python on purpose: returning nested lists
    # from C++ forces pybind11 to copy every token, which benchmarks slower than
    # slicing the existing Python string objects (scripts/benchmark_tokenizer.py).
    if n > len(normalized_tokens):
        return []
    return [tuple(normalized_tokens[index : index + n]) for index in range(len(normalized_tokens) - n + 1)]


def term_frequencies(tokens: list[str] | tuple[str, ...]) -> dict[str, int]:
    """Count token frequencies.

    Args:
        tokens (list[str] | tuple[str, ...]): Source token sequence.

    Returns:
        dict[str, int]: Token frequency mapping.
    """
    normalized_tokens = _normalize_iterable(tokens, name="tokens")
    if _CPP_BACKEND is not None:
        try:
            return dict(_CPP_BACKEND.count_term_frequencies(normalized_tokens))
        except (UnicodeError, ValueError):
            pass
    return dict(Counter(normalized_tokens))


def map_pos_tags(tags: list[str] | tuple[str, ...]) -> list[str]:
    """Map spaCy POS tags to the package's universal tagset.

    Args:
        tags (list[str] | tuple[str, ...]): POS tags to map.

    Returns:
        list[str]: Mapped POS tags.
    """
    normalized_tags = _normalize_iterable(tags, name="tags")
    return [POS_TAG_MAP.get(tag, tag) for tag in normalized_tags]


def stem_word(word: str) -> str:
    """Stem a single Portuguese word with the Snowball algorithm.

    The stemmer is accent-aware, so pass words with their original accents
    (for example from :func:`tokenize_text`, not the accent-folded
    :func:`normalize_text`).

    Args:
        word (str): Input word.

    Returns:
        str: The stemmed form.
    """
    return snowball_stem(_ensure_text(word, name="word"))


def stem_tokens(tokens: list[str] | tuple[str, ...]) -> list[str]:
    """Stem a sequence of tokens with the Snowball algorithm.

    Args:
        tokens (list[str] | tuple[str, ...]): Tokens to stem.

    Returns:
        list[str]: Stemmed tokens.
    """
    normalized_tokens = _normalize_iterable(tokens, name="tokens")
    return [snowball_stem(token) for token in normalized_tokens]


def stem_text(text: str) -> list[str]:
    """Tokenize Portuguese text and stem each token.

    Args:
        text (str): Input text.

    Returns:
        list[str]: Stemmed tokens, in order.
    """
    return [snowball_stem(token) for token in tokenize_text(_ensure_text(text))]


def _fold(value: str) -> str:
    """Accent-fold and lowercase a token for sentiment lookups.

    Args:
        value (str): Token to fold.

    Returns:
        str: Lower-case, accent-folded token.
    """
    return normalize_accents(value).lower()


# Accent-folded lookups so unaccented spellings also match the lexicon.
_SENTIMENT_LEXICON_FOLDED = {_fold(word): score for word, score in PORTUGUESE_SENTIMENT_LEXICON.items()}
_SENTIMENT_NEGATIONS_FOLDED = frozenset(_fold(word) for word in SENTIMENT_NEGATIONS)
_SENTIMENT_INTENSIFIERS_FOLDED = {_fold(word): factor for word, factor in SENTIMENT_INTENSIFIERS.items()}


def analyze_sentiment(text: str, *, negation_window: int = 3) -> SentimentScore:
    """Estimate sentiment polarity with a lexicon-based approach.

    Tokens are matched against a bundled polarity lexicon. A preceding
    intensifier (for example "muito") scales the next sentiment word, and a
    preceding negation (for example "não") inverts the polarity of the next
    ``negation_window`` sentiment words. Matching is accent-insensitive.

    Args:
        text (str): Input text.
        negation_window (int): Number of following words a negation affects.

    Returns:
        SentimentScore: Structured sentiment result.

    Raises:
        ValueError: If ``negation_window`` is negative.
    """
    if negation_window < 0:
        raise ValueError("`negation_window` must be non-negative")

    tokens = tokenize_text(_ensure_text(text))

    total = 0.0
    positive_tokens = 0
    negative_tokens = 0
    scored_tokens = 0
    negation_remaining = 0
    multiplier = 1.0

    for token in tokens:
        folded = _fold(token)

        if folded in _SENTIMENT_NEGATIONS_FOLDED:
            negation_remaining = negation_window
            multiplier = 1.0
            continue

        if folded in _SENTIMENT_INTENSIFIERS_FOLDED:
            multiplier *= _SENTIMENT_INTENSIFIERS_FOLDED[folded]
            continue

        if folded in _SENTIMENT_LEXICON_FOLDED:
            score = _SENTIMENT_LEXICON_FOLDED[folded] * multiplier
            if negation_remaining > 0:
                score = -score
                negation_remaining -= 1
            total += score
            scored_tokens += 1
            if score > 0:
                positive_tokens += 1
            elif score < 0:
                negative_tokens += 1
            multiplier = 1.0
        else:
            multiplier = 1.0
            if negation_remaining > 0:
                negation_remaining -= 1

    polarity = total / scored_tokens if scored_tokens else 0.0
    polarity = max(-1.0, min(1.0, polarity))
    if polarity > 0.05:
        label = "positive"
    elif polarity < -0.05:
        label = "negative"
    else:
        label = "neutral"

    return SentimentScore(
        polarity=polarity,
        label=label,
        positive_tokens=positive_tokens,
        negative_tokens=negative_tokens,
        token_count=len(tokens),
    )


def preprocess_text(
    text: str,
    *,
    correct: bool = False,
    remove_punct: bool = True,
    social: bool = False,
    custom_map: Mapping[str, str] | None = None,
    remove_stopwords: bool = False,
    use_spacy: bool = False,
) -> ProcessedText:
    """Run a high-level Portuguese preprocessing pipeline.

    Args:
        text (str): Input text.
        correct (bool): Whether to apply orthographic corrections.
        remove_punct (bool): Whether to remove punctuation during normalization.
        social (bool): Whether to apply social-text cleaning before normalization.
        custom_map (Mapping[str, str] | None): Optional slang overrides.
        remove_stopwords (bool): Whether to remove stopwords from the token list.
        use_spacy (bool): Whether to use spaCy tokenization and sentence segmentation.

    Returns:
        ProcessedText: Structured preprocessing output.
    """
    original_text = _ensure_text(text)
    working_text = original_text

    if social:
        working_text = clean_social_text(
            working_text,
            emoji=True,
            accents=False,
            slang=True,
            custom_map=custom_map,
        )

    normalized_text = normalize_text(
        working_text,
        lower=True,
        remove_punct=remove_punct,
        correct=correct,
    )

    if use_spacy:
        from ._spacy import spacy_sentencize, spacy_tokenize

        sentences = spacy_sentencize(working_text)
        tokens = spacy_tokenize(normalized_text)
    else:
        sentences = tokenize_text(working_text, kind="sentence")
        tokens = tokenize_text(normalized_text, kind="word")

    # Tokens are accent-folded by normalize_text, so match stopwords
    # accent-insensitively to also catch entries like "não" or "às".
    filtered_tokens = filter_stopwords(tokens, normalize=True) if remove_stopwords else list(tokens)
    return ProcessedText(
        original_text=original_text,
        normalized_text=normalized_text,
        sentences=sentences,
        tokens=tokens,
        filtered_tokens=filtered_tokens,
    )


def analyze_corpus(
    texts: list[str] | tuple[str, ...],
    *,
    correct: bool = False,
    remove_punct: bool = True,
    social: bool = False,
    custom_map: Mapping[str, str] | None = None,
    remove_stopwords: bool = False,
    use_spacy: bool = False,
    ngram_size: int = 2,
) -> CorpusStatistics:
    """Aggregate token and n-gram statistics for multiple texts.

    Args:
        texts (list[str] | tuple[str, ...]): Input documents.
        correct (bool): Whether to apply orthographic corrections.
        remove_punct (bool): Whether to remove punctuation during normalization.
        social (bool): Whether to apply social-text cleaning before normalization.
        custom_map (Mapping[str, str] | None): Optional slang overrides.
        remove_stopwords (bool): Whether to remove stopwords before aggregation.
        use_spacy (bool): Whether to use spaCy tokenization and sentence segmentation.
        ngram_size (int): Size of contiguous n-grams to count.

    Returns:
        CorpusStatistics: Aggregate corpus statistics.
    """
    normalized_texts = _ensure_texts(texts)
    if ngram_size < 1:
        raise ValueError("`ngram_size` must be at least 1")

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

    aggregated_tokens: list[str] = []
    for document in processed_documents:
        aggregated_tokens.extend(document.filtered_tokens if remove_stopwords else document.tokens)

    frequencies = term_frequencies(aggregated_tokens)
    ngram_counter: Counter[tuple[str, ...]] = Counter()
    for document in processed_documents:
        source_tokens = document.filtered_tokens if remove_stopwords else document.tokens
        ngram_counter.update(generate_ngrams(source_tokens, ngram_size))

    return CorpusStatistics(
        document_count=len(processed_documents),
        token_count=len(aggregated_tokens),
        unique_token_count=len(frequencies),
        frequencies=frequencies,
        ngrams=dict(ngram_counter),
    )


def compute_inverse_document_frequency(
    texts: list[str] | tuple[str, ...],
    *,
    correct: bool = False,
    remove_punct: bool = True,
    social: bool = False,
    custom_map: Mapping[str, str] | None = None,
    remove_stopwords: bool = False,
    use_spacy: bool = False,
) -> dict[str, float]:
    """Compute smoothed inverse document frequency values for a corpus.

    Args:
        texts (list[str] | tuple[str, ...]): Input documents.
        correct (bool): Whether to apply orthographic corrections.
        remove_punct (bool): Whether to remove punctuation during normalization.
        social (bool): Whether to apply social-text cleaning before normalization.
        custom_map (Mapping[str, str] | None): Optional slang overrides.
        remove_stopwords (bool): Whether to remove stopwords before scoring.
        use_spacy (bool): Whether to use spaCy tokenization and sentence segmentation.

    Returns:
        dict[str, float]: Smoothed IDF values by token.
    """
    normalized_texts = _ensure_texts(texts)
    if not normalized_texts:
        return {}

    document_frequencies: Counter[str] = Counter()
    for text in normalized_texts:
        processed = preprocess_text(
            text,
            correct=correct,
            remove_punct=remove_punct,
            social=social,
            custom_map=custom_map,
            remove_stopwords=remove_stopwords,
            use_spacy=use_spacy,
        )
        source_tokens = processed.filtered_tokens if remove_stopwords else processed.tokens
        document_frequencies.update(set(source_tokens))

    total_documents = len(normalized_texts)
    return {
        token: math.log((1 + total_documents) / (1 + document_frequency)) + 1.0
        for token, document_frequency in document_frequencies.items()
    }


def extract_keywords(
    text: str,
    *,
    corpus: list[str] | tuple[str, ...] | None = None,
    top_k: int = 10,
    correct: bool = False,
    remove_punct: bool = True,
    social: bool = False,
    custom_map: Mapping[str, str] | None = None,
    remove_stopwords: bool = True,
    use_spacy: bool = False,
) -> list[KeywordScore]:
    """Extract weighted keywords from a text using TF-IDF-style scoring.

    Args:
        text (str): Input document.
        corpus (list[str] | tuple[str, ...] | None): Optional corpus for IDF estimation.
        top_k (int): Maximum number of keywords to return.
        correct (bool): Whether to apply orthographic corrections.
        remove_punct (bool): Whether to remove punctuation during normalization.
        social (bool): Whether to apply social-text cleaning before normalization.
        custom_map (Mapping[str, str] | None): Optional slang overrides.
        remove_stopwords (bool): Whether to remove stopwords before scoring.
        use_spacy (bool): Whether to use spaCy tokenization and sentence segmentation.

    Returns:
        list[KeywordScore]: Ranked keyword scores.
    """
    if top_k < 1:
        raise ValueError("`top_k` must be at least 1")

    processed = preprocess_text(
        text,
        correct=correct,
        remove_punct=remove_punct,
        social=social,
        custom_map=custom_map,
        remove_stopwords=remove_stopwords,
        use_spacy=use_spacy,
    )
    tokens = processed.filtered_tokens if remove_stopwords else processed.tokens
    if not tokens:
        return []

    frequencies = term_frequencies(tokens)
    reference_corpus = [text] if corpus is None else [text, *_ensure_texts(corpus)]
    idf_values = compute_inverse_document_frequency(
        reference_corpus,
        correct=correct,
        remove_punct=remove_punct,
        social=social,
        custom_map=custom_map,
        remove_stopwords=remove_stopwords,
        use_spacy=use_spacy,
    )

    token_count = len(tokens)
    scores = [
        KeywordScore(
            token=token,
            score=(frequency / token_count) * idf_values.get(token, 1.0),
        )
        for token, frequency in frequencies.items()
    ]
    return sorted(scores, key=lambda keyword: (-keyword.score, keyword.token))[:top_k]


def _build_tfidf_vector(
    text: str,
    *,
    corpus: list[str],
    correct: bool,
    remove_punct: bool,
    social: bool,
    custom_map: Mapping[str, str] | None,
    remove_stopwords: bool,
    use_spacy: bool,
) -> dict[str, float]:
    """Build a TF-IDF vector for a single document.

    Args:
        text (str): Input document.
        corpus (list[str]): Reference corpus including the document.
        correct (bool): Whether to apply orthographic corrections.
        remove_punct (bool): Whether to remove punctuation during normalization.
        social (bool): Whether to apply social-text cleaning before normalization.
        custom_map (Mapping[str, str] | None): Optional slang overrides.
        remove_stopwords (bool): Whether to remove stopwords before scoring.
        use_spacy (bool): Whether to use spaCy tokenization and sentence segmentation.

    Returns:
        dict[str, float]: TF-IDF vector keyed by token.
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
    tokens = processed.filtered_tokens if remove_stopwords else processed.tokens
    if not tokens:
        return {}

    frequencies = term_frequencies(tokens)
    idf_values = compute_inverse_document_frequency(
        corpus,
        correct=correct,
        remove_punct=remove_punct,
        social=social,
        custom_map=custom_map,
        remove_stopwords=remove_stopwords,
        use_spacy=use_spacy,
    )
    token_count = len(tokens)
    return {
        token: (frequency / token_count) * idf_values.get(token, 1.0)
        for token, frequency in frequencies.items()
    }


def _cosine_similarity(left: dict[str, float], right: dict[str, float]) -> float:
    """Compute cosine similarity between sparse vectors.

    Args:
        left (dict[str, float]): Left sparse vector.
        right (dict[str, float]): Right sparse vector.

    Returns:
        float: Cosine similarity score.
    """
    if not left or not right:
        return 0.0

    shared_tokens = set(left).intersection(right)
    numerator = sum(left[token] * right[token] for token in shared_tokens)
    left_norm = math.sqrt(sum(value * value for value in left.values()))
    right_norm = math.sqrt(sum(value * value for value in right.values()))

    if left_norm == 0.0 or right_norm == 0.0:
        return 0.0
    return numerator / (left_norm * right_norm)


def compare_texts(
    text: str,
    other_text: str,
    *,
    corpus: list[str] | tuple[str, ...] | None = None,
    correct: bool = False,
    remove_punct: bool = True,
    social: bool = False,
    custom_map: Mapping[str, str] | None = None,
    remove_stopwords: bool = True,
    use_spacy: bool = False,
) -> float:
    """Compare two texts with cosine similarity over TF-IDF vectors.

    Args:
        text (str): First document.
        other_text (str): Second document.
        corpus (list[str] | tuple[str, ...] | None): Optional extra corpus for IDF estimation.
        correct (bool): Whether to apply orthographic corrections.
        remove_punct (bool): Whether to remove punctuation during normalization.
        social (bool): Whether to apply social-text cleaning before normalization.
        custom_map (Mapping[str, str] | None): Optional slang overrides.
        remove_stopwords (bool): Whether to remove stopwords before scoring.
        use_spacy (bool): Whether to use spaCy tokenization and sentence segmentation.

    Returns:
        float: Cosine similarity score in the range [0.0, 1.0].
    """
    first_text = _ensure_text(text)
    second_text = _ensure_text(other_text)
    reference_corpus = [first_text, second_text]
    if corpus is not None:
        reference_corpus.extend(_ensure_texts(corpus, name="corpus"))

    left_vector = _build_tfidf_vector(
        first_text,
        corpus=reference_corpus,
        correct=correct,
        remove_punct=remove_punct,
        social=social,
        custom_map=custom_map,
        remove_stopwords=remove_stopwords,
        use_spacy=use_spacy,
    )
    right_vector = _build_tfidf_vector(
        second_text,
        corpus=reference_corpus,
        correct=correct,
        remove_punct=remove_punct,
        social=social,
        custom_map=custom_map,
        remove_stopwords=remove_stopwords,
        use_spacy=use_spacy,
    )
    return _cosine_similarity(left_vector, right_vector)


def rank_similar_texts(
    query: str,
    texts: list[str] | tuple[str, ...],
    *,
    top_k: int = 5,
    correct: bool = False,
    remove_punct: bool = True,
    social: bool = False,
    custom_map: Mapping[str, str] | None = None,
    remove_stopwords: bool = True,
    use_spacy: bool = False,
) -> list[SimilarityScore]:
    """Rank corpus documents by similarity to a query document.

    Args:
        query (str): Query document.
        texts (list[str] | tuple[str, ...]): Candidate documents.
        top_k (int): Maximum number of matches to return.
        correct (bool): Whether to apply orthographic corrections.
        remove_punct (bool): Whether to remove punctuation during normalization.
        social (bool): Whether to apply social-text cleaning before normalization.
        custom_map (Mapping[str, str] | None): Optional slang overrides.
        remove_stopwords (bool): Whether to remove stopwords before scoring.
        use_spacy (bool): Whether to use spaCy tokenization and sentence segmentation.

    Returns:
        list[SimilarityScore]: Ranked similarity matches.
    """
    if top_k < 1:
        raise ValueError("`top_k` must be at least 1")

    query_text = _ensure_text(query, name="query")
    candidates = _ensure_texts(texts)
    if not candidates:
        return []

    reference_corpus = [query_text, *candidates]
    query_vector = _build_tfidf_vector(
        query_text,
        corpus=reference_corpus,
        correct=correct,
        remove_punct=remove_punct,
        social=social,
        custom_map=custom_map,
        remove_stopwords=remove_stopwords,
        use_spacy=use_spacy,
    )

    scored_documents = [
        SimilarityScore(
            index=index,
            text=document,
            score=_cosine_similarity(
                query_vector,
                _build_tfidf_vector(
                    document,
                    corpus=reference_corpus,
                    correct=correct,
                    remove_punct=remove_punct,
                    social=social,
                    custom_map=custom_map,
                    remove_stopwords=remove_stopwords,
                    use_spacy=use_spacy,
                ),
            ),
        )
        for index, document in enumerate(candidates)
    ]
    return sorted(scored_documents, key=lambda match: (-match.score, match.index))[:top_k]


def analyze_text_metrics(
    text: str,
    *,
    correct: bool = False,
    remove_punct: bool = True,
    social: bool = False,
    custom_map: Mapping[str, str] | None = None,
    remove_stopwords: bool = False,
    use_spacy: bool = False,
) -> TextStatistics:
    """Compute descriptive and readability metrics for a text.

    Args:
        text (str): Input document.
        correct (bool): Whether to apply orthographic corrections.
        remove_punct (bool): Whether to remove punctuation during normalization.
        social (bool): Whether to apply social-text cleaning before normalization.
        custom_map (Mapping[str, str] | None): Optional slang overrides.
        remove_stopwords (bool): Whether to remove stopwords before analysis.
        use_spacy (bool): Whether to use spaCy tokenization and sentence segmentation.

    Returns:
        TextStatistics: Structured text metrics.
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
    tokens = processed.filtered_tokens if remove_stopwords else processed.tokens
    sentence_count = len(processed.sentences)
    token_count = len(tokens)
    unique_token_count = len(set(tokens))
    character_count = len(processed.normalized_text)
    syllable_count = sum(_count_syllables(token) for token in tokens)

    average_token_length = (
        sum(len(token) for token in tokens) / token_count if token_count else 0.0
    )
    average_sentence_length = token_count / sentence_count if sentence_count else 0.0
    lexical_diversity = unique_token_count / token_count if token_count else 0.0
    average_syllables_per_word = syllable_count / token_count if token_count else 0.0
    flesch_reading_ease = (
        248.835 - (1.015 * average_sentence_length) - (84.6 * average_syllables_per_word)
        if token_count and sentence_count
        else 0.0
    )

    return TextStatistics(
        sentence_count=sentence_count,
        token_count=token_count,
        unique_token_count=unique_token_count,
        character_count=character_count,
        average_token_length=average_token_length,
        average_sentence_length=average_sentence_length,
        lexical_diversity=lexical_diversity,
        syllable_count=syllable_count,
        average_syllables_per_word=average_syllables_per_word,
        flesch_reading_ease=flesch_reading_ease,
    )


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
