from pathlib import Path

import pytest

from portunlp import (
    CorpusStatistics,
    KeywordScore,
    PORTUGUESE_STOPWORDS,
    ProcessedText,
    SimilarityScore,
    TextStatistics,
    analyze_text_metrics,
    analyze_corpus,
    apply_orth_rules,
    clean_social,
    compare_texts,
    compute_inverse_document_frequency,
    extract_keywords,
    filter_stopwords,
    generate_ngrams,
    get_stopwords,
    load_dict,
    map_pos_tags,
    map_slang,
    normalize_accents,
    normalize_text,
    preprocess_text,
    rank_similar_texts,
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


def test_compute_inverse_document_frequency_scores_rarer_terms_higher() -> None:
    """IDF assigns higher weights to rarer tokens."""
    idf = compute_inverse_document_frequency(["casa bonita", "casa azul"])
    assert idf["bonita"] > idf["casa"]
    assert idf["azul"] > idf["casa"]


def test_extract_keywords_returns_ranked_keyword_scores() -> None:
    """Keyword extraction returns scored tokens ordered by relevance."""
    keywords = extract_keywords(
        "A casa bonita e bonita",
        corpus=["A casa azul", "Casa verde"],
        top_k=2,
    )
    assert all(isinstance(keyword, KeywordScore) for keyword in keywords)
    assert keywords[0].token == "bonita"
    assert len(keywords) == 2


def test_extract_keywords_validates_top_k() -> None:
    """Keyword extraction rejects invalid top-k values."""
    with pytest.raises(ValueError, match="`top_k` must be at least 1"):
        extract_keywords("texto", top_k=0)


def test_compare_texts_scores_similar_documents_higher() -> None:
    """Similarity scoring favors semantically closer token overlap."""
    similar_score = compare_texts("casa bonita azul", "casa azul")
    different_score = compare_texts("casa bonita azul", "carro veloz")

    assert similar_score > different_score
    assert 0.0 <= similar_score <= 1.0


def test_rank_similar_texts_orders_best_matches_first() -> None:
    """Document ranking returns the best match at the top."""
    matches = rank_similar_texts(
        "casa azul bonita",
        ["carro veloz", "casa azul", "casa verde"],
        top_k=2,
    )

    assert all(isinstance(match, SimilarityScore) for match in matches)
    assert [match.index for match in matches] == [1, 2]
    assert matches[0].text == "casa azul"
    assert matches[0].score >= matches[1].score


def test_rank_similar_texts_validates_top_k() -> None:
    """Document ranking rejects invalid top-k values."""
    with pytest.raises(ValueError, match="`top_k` must be at least 1"):
        rank_similar_texts("texto", ["outro"], top_k=0)


def test_analyze_text_metrics_returns_structured_statistics() -> None:
    """Text metrics expose descriptive counts and readability values."""
    metrics = analyze_text_metrics("A casa bonita. A casa azul.")

    assert isinstance(metrics, TextStatistics)
    assert metrics.sentence_count == 2
    assert metrics.token_count == 6
    assert metrics.unique_token_count == 4
    assert metrics.lexical_diversity == pytest.approx(4 / 6)
    assert metrics.syllable_count > 0
    assert metrics.average_sentence_length == pytest.approx(3.0)


def test_analyze_text_metrics_can_remove_stopwords() -> None:
    """Text metrics can be computed from stopword-filtered tokens."""
    metrics = analyze_text_metrics("A casa e bonita", remove_stopwords=True)

    assert metrics.token_count == 2
    assert metrics.unique_token_count == 2
    assert metrics.average_token_length == pytest.approx(5.0)


def test_analyze_text_metrics_handles_empty_text() -> None:
    """Empty input returns zeroed metrics instead of failing."""
    metrics = analyze_text_metrics("")

    assert metrics == TextStatistics(
        sentence_count=0,
        token_count=0,
        unique_token_count=0,
        character_count=0,
        average_token_length=0.0,
        average_sentence_length=0.0,
        lexical_diversity=0.0,
        syllable_count=0,
        average_syllables_per_word=0.0,
        flesch_reading_ease=0.0,
    )


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
