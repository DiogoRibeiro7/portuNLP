from pathlib import Path

import pytest

from portunlp import (
    CorpusStatistics,
    PORTUGUESE_STOPWORDS,
    ProcessedText,
    analyze_corpus,
    apply_orth_rules,
    clean_social,
    filter_stopwords,
    generate_ngrams,
    get_stopwords,
    load_dict,
    map_pos_tags,
    map_slang,
    normalize_accents,
    normalize_text,
    preprocess_text,
    remove_emoji,
    term_frequencies,
    tokenize_pt,
    tokenize_text,
)
from portunlp import text as text_module


def test_normalize_text_applies_expected_steps() -> None:
    """Normalization lowercases, corrects, and folds accents."""
    assert normalize_text("Acção", correct=True) == "acao"
    assert normalize_text("Olá, Mundo!", remove_punct=True) == "ola mundo"


def test_tokenize_text_supports_word_and_sentence_modes() -> None:
    """Native tokenization handles words and sentences."""
    assert tokenize_text("Olá, mundo! Tudo bem?") == ["olá", "mundo", "tudo", "bem"]
    assert tokenize_text("Olá. Tudo bem?", kind="sentence") == ["Olá.", "Tudo bem?"]
    assert tokenize_pt("Olá, mundo!") == ["olá", "mundo"]


def test_remove_emoji_and_map_slang() -> None:
    """Social helpers remove emoji and replace whole-word slang."""
    assert remove_emoji("Olá 😊") == "Olá "
    assert map_slang("vc tá blz", custom_map={"tá": "está"}) == "você está beleza"
    assert map_slang("svc", custom_map={"vc": "você"}) == "svc"


def test_clean_social_combines_social_transformations() -> None:
    """The social cleaning pipeline applies all enabled transformations."""
    result = clean_social("vc tá 😊", custom_map={"tá": "está"})
    assert result == "voce esta "


def test_get_stopwords_supports_additions_and_omissions() -> None:
    """Stopword retrieval preserves built-ins and applies overrides."""
    words = get_stopwords(extra={"novapalavra"}, omit={"não"})
    assert "a" in words
    assert "novapalavra" in words
    assert "não" not in words
    assert PORTUGUESE_STOPWORDS[0] == "a"


def test_filter_stopwords_removes_configured_words() -> None:
    """Stopword filtering removes built-in and custom stopwords."""
    assert filter_stopwords(["a", "casa", "e", "bonita"]) == ["casa", "bonita"]
    assert filter_stopwords(["ação", "bonita"], stopwords={"acao"}, normalize=True) == ["bonita"]


def test_generate_ngrams_builds_contiguous_sequences() -> None:
    """N-gram generation preserves order and contiguity."""
    assert generate_ngrams(["um", "dois", "tres"], 2) == [("um", "dois"), ("dois", "tres")]
    assert generate_ngrams(["um"], 2) == []


def test_term_frequencies_counts_tokens() -> None:
    """Token frequency counting aggregates repeated tokens."""
    assert term_frequencies(["casa", "casa", "bonita"]) == {"casa": 2, "bonita": 1}


def test_load_dict_reads_non_empty_lines(tmp_path: Path) -> None:
    """Dictionary loading trims whitespace and skips blanks."""
    dictionary_path = tmp_path / "sample_dict.txt"
    dictionary_path.write_text(" ola\n\nmundo \n", encoding="utf-8")

    assert load_dict(dictionary_path) == ["ola", "mundo"]


def test_load_dict_errors_for_missing_file(tmp_path: Path) -> None:
    """Missing dictionary files raise a clear error."""
    with pytest.raises(FileNotFoundError, match="File not found"):
        load_dict(tmp_path / "missing.txt")


def test_map_pos_tags_preserves_unknown_values() -> None:
    """Known tags are mapped and unknown tags pass through unchanged."""
    assert map_pos_tags(["NOUN", "UNKNOWN"]) == ["NOUN", "UNKNOWN"]


def test_preprocess_text_builds_structured_result() -> None:
    """The preprocessing pipeline returns normalized, tokenized outputs."""
    result = preprocess_text("Acção e vc! 😊", correct=True, social=True, remove_stopwords=True)
    assert isinstance(result, ProcessedText)
    assert result.original_text == "Acção e vc! 😊"
    assert result.normalized_text == "acao e voce "
    assert result.sentences == ["Acção e você!"]
    assert result.tokens == ["acao", "e", "voce"]
    assert result.filtered_tokens == ["acao", "voce"]


def test_preprocess_text_uses_native_sentence_segmentation_by_default() -> None:
    """The preprocessing pipeline preserves simple sentence boundaries."""
    result = preprocess_text("Olá. Tudo bem?", remove_punct=False)
    assert result.sentences == ["Olá.", "Tudo bem?"]
    assert result.tokens == ["ola", "tudo", "bem"]


def test_analyze_corpus_aggregates_document_statistics() -> None:
    """Corpus analysis aggregates frequencies and n-grams across documents."""
    result = analyze_corpus(
        ["A casa bonita", "A casa azul"],
        remove_stopwords=True,
        ngram_size=2,
    )
    assert isinstance(result, CorpusStatistics)
    assert result.document_count == 2
    assert result.token_count == 4
    assert result.unique_token_count == 3
    assert result.frequencies == {"casa": 2, "bonita": 1, "azul": 1}
    assert result.ngrams == {("casa", "bonita"): 1, ("casa", "azul"): 1}


def test_analyze_corpus_validates_ngram_size() -> None:
    """Corpus analysis rejects invalid n-gram sizes."""
    with pytest.raises(ValueError, match="`ngram_size` must be at least 1"):
        analyze_corpus(["texto"], ngram_size=0)


def test_normalize_accents_and_apply_orth_rules() -> None:
    """Accent folding and orthographic replacements work independently."""
    assert normalize_accents("ação") == "acao"
    assert apply_orth_rules("acto electrico") == "ato elétrico"


def test_text_helpers_validate_argument_types() -> None:
    """Public helpers reject non-string inputs."""
    with pytest.raises(TypeError, match="`text` must be a string"):
        normalize_text(123)  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="`custom_map` must map strings to strings"):
        map_slang("texto", custom_map={"vc": 1})  # type: ignore[dict-item]


def test_cpp_backend_is_loaded_for_heavy_helpers() -> None:
    """The compiled backend is available for token and corpus helpers."""
    assert text_module._CPP_BACKEND is not None
