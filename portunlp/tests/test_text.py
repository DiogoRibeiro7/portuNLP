from pathlib import Path
import json

import pytest

from portunlp import (
    CorpusAnalysis,
    CorpusStatistics,
    KeywordScore,
    PORTUGUESE_STOPWORDS,
    ProcessedText,
    SimilarityScore,
    TextAnalysis,
    TextStatistics,
    analysis_to_dict,
    analysis_to_json,
    analyze_text,
    analyze_sentiment,
    analyze_text_metrics,
    analyze_texts,
    analyze_corpus,
    apply_orthographic_rules,
    clean_social_text,
    compare_texts,
    compute_inverse_document_frequency,
    expand_contractions,
    extract_keywords,
    filter_stopwords,
    generate_ngrams,
    get_stopwords,
    load_dictionary,
    map_pos_tags,
    map_slang,
    normalize_accents,
    normalize_text,
    preprocess_text,
    rank_similar_texts,
    remove_emoji,
    stem_text,
    stem_tokens,
    stem_word,
    term_frequencies,
    tokenize_text,
)
from portunlp import text as text_module
from portunlp import _spacy as spacy_module


def test_normalize_text_applies_expected_steps() -> None:
    """Normalization lowercases, corrects, and folds accents."""
    assert normalize_text("Acção", correct=True) == "acao"
    assert normalize_text("Olá, Mundo!", remove_punct=True) == "ola mundo"


def test_tokenize_text_supports_word_and_sentence_modes() -> None:
    """Native tokenization handles words and sentences."""
    assert tokenize_text("Olá, mundo! Tudo bem?") == ["olá", "mundo", "tudo", "bem"]
    assert tokenize_text("Olá. Tudo bem?", kind="sentence") == ["Olá.", "Tudo bem?"]
    assert tokenize_text("Olá, mundo!") == ["olá", "mundo"]


def test_remove_emoji_and_map_slang() -> None:
    """Social helpers remove emoji and replace whole-word slang."""
    assert remove_emoji("Olá 😊") == "Olá "
    assert map_slang("vc tá blz", custom_map={"tá": "está"}) == "você está beleza"
    assert map_slang("svc", custom_map={"vc": "você"}) == "svc"


def test_clean_social_combines_social_transformations() -> None:
    """The social cleaning pipeline applies all enabled transformations."""
    result = clean_social_text("vc tá 😊", custom_map={"tá": "está"})
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


def test_preprocess_removes_accented_stopwords() -> None:
    """Accent-folded tokens still match accented stopwords like 'não'/'à'."""
    result = preprocess_text("Eu não vou à praia mas você sim", remove_stopwords=True)
    assert result.filtered_tokens == ["vou", "praia", "sim"]


def test_expand_contractions_expands_known_forms() -> None:
    """Preposition contractions expand to their two-word components."""
    assert expand_contractions("Fui ao mercado do bairro") == "Fui a o mercado de o bairro"
    assert expand_contractions("Está na casa da Maria") == "Está em a casa de a Maria"
    assert expand_contractions("Penso nisso e naquilo") == "Penso em isso e em aquilo"
    assert expand_contractions("Falei pelos cotovelos") == "Falei por os cotovelos"


def test_expand_contractions_handles_accents_and_custom_map() -> None:
    """Accented contractions expand and custom overrides apply."""
    assert expand_contractions("Dei àquele homem") == "Dei a aquele homem"
    assert expand_contractions("co", custom_map={"co": "com o"}) == "com o"
    with pytest.raises(TypeError, match="`custom_map` must map strings to strings"):
        expand_contractions("do", custom_map={"do": 1})  # type: ignore[dict-item]


def test_stem_word_matches_snowball_reference() -> None:
    """Stemming reduces inflected forms (Snowball Portuguese algorithm)."""
    assert stem_word("meninos") == "menin"
    assert stem_word("rapidamente") == "rapid"
    assert stem_word("trabalhador") == "trabalh"
    assert stem_word("países") == "país"
    assert stem_word("Cantando") == "cant"
    assert stem_word("nação") == "naçã"


def test_stem_tokens_and_text() -> None:
    """Token- and text-level stemming preserve order."""
    assert stem_tokens(["casas", "bonitas"]) == ["cas", "bonit"]
    assert stem_text("Os gatos corriam felizes") == ["os", "gat", "corr", "feliz"]


def test_stem_word_validates_type() -> None:
    """Stemming rejects non-string input."""
    with pytest.raises(TypeError, match="`word` must be a string"):
        stem_word(123)  # type: ignore[arg-type]


def test_analyze_sentiment_basic_polarity() -> None:
    """Positive and negative texts get the expected labels and polarity."""
    positive = analyze_sentiment("Este produto é excelente e maravilhoso!")
    assert positive.label == "positive"
    assert positive.polarity == 1.0
    assert positive.positive_tokens == 2

    negative = analyze_sentiment("O atendimento foi péssimo e horrível.")
    assert negative.label == "negative"
    assert negative.polarity == -1.0
    assert negative.negative_tokens == 2

    neutral = analyze_sentiment("A reunião começou às nove horas.")
    assert neutral.label == "neutral"
    assert neutral.polarity == 0.0


def test_analyze_sentiment_handles_negation_and_intensifiers() -> None:
    """Negation inverts polarity and intensifiers scale it."""
    assert analyze_sentiment("Não gostei do filme.").polarity == -0.7
    assert analyze_sentiment("O serviço foi muito bom.").polarity == 1.0
    # Unaccented spelling still matches the lexicon.
    assert analyze_sentiment("Que filme otimo").label == "positive"


def test_analyze_sentiment_validates_window() -> None:
    """A negative negation window is rejected."""
    with pytest.raises(ValueError, match="`negation_window` must be non-negative"):
        analyze_sentiment("texto", negation_window=-1)


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

    assert load_dictionary(dictionary_path) == ["ola", "mundo"]


def test_load_dict_errors_for_missing_file(tmp_path: Path) -> None:
    """Missing dictionary files raise a clear error."""
    with pytest.raises(FileNotFoundError, match="File not found"):
        load_dictionary(tmp_path / "missing.txt")


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
    # "e" and "você" (folded "voce") are stopwords; accent-insensitive filtering
    # removes both, leaving the content word.
    assert result.filtered_tokens == ["acao"]


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


def test_analyze_text_returns_composed_result() -> None:
    """High-level text analysis composes preprocessing, metrics, and keywords."""
    result = analyze_text("A casa bonita", remove_stopwords=True, keyword_top_k=2)

    assert isinstance(result, TextAnalysis)
    assert result.text == "A casa bonita"
    assert result.processed.filtered_tokens == ["casa", "bonita"]
    assert result.metrics.token_count == 2
    assert len(result.keywords) <= 2
    assert result.spacy_document is None
    assert result.spacy_lexicon is None
    assert result.spacy_collocations is None


def test_analyze_texts_returns_composed_corpus_result() -> None:
    """High-level corpus analysis composes preprocessing and aggregate stats."""
    result = analyze_texts(["A casa bonita", "A casa azul"], remove_stopwords=True)

    assert isinstance(result, CorpusAnalysis)
    assert result.texts == ["A casa bonita", "A casa azul"]
    assert len(result.processed_documents) == 2
    assert result.statistics.frequencies == {"casa": 2, "bonita": 1, "azul": 1}
    assert result.idf_values["bonita"] > result.idf_values["casa"]
    assert result.spacy_corpus is None
    assert result.spacy_lexicon is None
    assert result.spacy_collocations is None


def test_analyze_text_can_include_spacy_sections(monkeypatch: pytest.MonkeyPatch) -> None:
    """High-level text analysis can include optional spaCy summaries."""
    document_summary = spacy_module.SpacyDocument(
        text="texto",
        tokens=[],
        morphology=spacy_module.SpacyMorphology(tokens=[], lemmas=[], pos_counts={}, morph_counts={}),
        entities=spacy_module.SpacyEntities(entities=[], label_counts={}),
        dependencies=spacy_module.SpacyDependencies(tokens=[], root="", dep_counts={}),
        noun_chunks=spacy_module.SpacyNounChunks(chunks=[], root_counts={}),
        sentences=spacy_module.SpacySentences(sentences=[], sentence_count=0),
    )
    lexicon_summary = spacy_module.SpacyLexicon(
        token_frequencies={"texto": 1},
        lemma_frequencies={"texto": 1},
        lemmas_by_pos={"NOUN": {"texto": 1}},
    )
    collocation_summary = spacy_module.SpacyCollocations(
        n=2,
        collocations=[spacy_module.SpacyCollocation(terms=["texto", "bom"], count=1)],
    )

    monkeypatch.setattr(spacy_module, "spacy_document", lambda text: document_summary)
    monkeypatch.setattr(spacy_module, "spacy_lexicon", lambda text: lexicon_summary)
    monkeypatch.setattr(spacy_module, "spacy_collocations", lambda text, n=2: collocation_summary)

    result = analyze_text(
        "texto",
        include_spacy=True,
        include_spacy_lexicon=True,
        include_spacy_collocations=True,
    )

    assert result.spacy_document is document_summary
    assert result.spacy_lexicon is lexicon_summary
    assert result.spacy_collocations is collocation_summary


def test_analyze_texts_can_include_spacy_sections(monkeypatch: pytest.MonkeyPatch) -> None:
    """High-level corpus analysis can include optional spaCy summaries."""
    corpus_summary = spacy_module.SpacyCorpus(
        documents=[],
        document_count=2,
        token_count=3,
        pos_counts={"NOUN": 3},
        entity_label_counts={},
        dependency_counts={},
        noun_chunk_root_counts={},
    )
    lexicon_summary = spacy_module.SpacyLexiconCorpus(
        document_count=2,
        token_frequencies={"casa": 2},
        lemma_frequencies={"casa": 2},
        lemmas_by_pos={"NOUN": {"casa": 2}},
    )
    collocation_summary = spacy_module.SpacyCollocationCorpus(
        document_count=2,
        n=2,
        collocations=[spacy_module.SpacyCollocation(terms=["casa", "bonita"], count=1)],
    )

    monkeypatch.setattr(spacy_module, "spacy_corpus", lambda texts: corpus_summary)
    monkeypatch.setattr(spacy_module, "spacy_lexicon_corpus", lambda texts: lexicon_summary)
    monkeypatch.setattr(spacy_module, "spacy_collocations_corpus", lambda texts, n=2: collocation_summary)

    result = analyze_texts(
        ["A casa bonita", "A casa azul"],
        include_spacy=True,
        include_spacy_lexicon=True,
        include_spacy_collocations=True,
    )

    assert result.spacy_corpus is corpus_summary
    assert result.spacy_lexicon is lexicon_summary
    assert result.spacy_collocations is collocation_summary


def test_analysis_to_dict_serializes_text_analysis() -> None:
    """High-level text analysis can be serialized into nested dictionaries."""
    result = analyze_text("A casa bonita", remove_stopwords=True, keyword_top_k=2)
    payload = analysis_to_dict(result)

    assert payload["text"] == "A casa bonita"
    assert isinstance(payload["processed"], dict)
    assert isinstance(payload["metrics"], dict)
    assert isinstance(payload["keywords"], list)


def test_analysis_to_json_serializes_corpus_analysis() -> None:
    """High-level corpus analysis can be serialized into JSON."""
    result = analyze_texts(["A casa bonita", "A casa azul"], remove_stopwords=True)
    payload = json.loads(analysis_to_json(result, indent=None))

    assert payload["texts"] == ["A casa bonita", "A casa azul"]
    assert payload["statistics"]["frequencies"] == {"casa": 2, "bonita": 1, "azul": 1}


def test_analysis_to_dict_keeps_optional_spacy_sections(monkeypatch: pytest.MonkeyPatch) -> None:
    """Serialization preserves optional mocked spaCy sections."""
    document_summary = spacy_module.SpacyDocument(
        text="texto",
        tokens=[],
        morphology=spacy_module.SpacyMorphology(tokens=[], lemmas=[], pos_counts={}, morph_counts={}),
        entities=spacy_module.SpacyEntities(entities=[], label_counts={}),
        dependencies=spacy_module.SpacyDependencies(tokens=[], root="", dep_counts={}),
        noun_chunks=spacy_module.SpacyNounChunks(chunks=[], root_counts={}),
        sentences=spacy_module.SpacySentences(sentences=[], sentence_count=0),
    )

    monkeypatch.setattr(spacy_module, "spacy_document", lambda text: document_summary)

    result = analyze_text("texto", include_spacy=True)
    payload = analysis_to_dict(result)

    spacy_payload = payload["spacy_document"]
    assert isinstance(spacy_payload, dict)
    assert spacy_payload["text"] == "texto"


def test_normalize_accents_and_apply_orth_rules() -> None:
    """Accent folding and orthographic replacements work independently."""
    assert normalize_accents("ação") == "acao"
    assert apply_orthographic_rules("acto electrico") == "ato elétrico"


def test_text_helpers_validate_argument_types() -> None:
    """Public helpers reject non-string inputs."""
    with pytest.raises(TypeError, match="`text` must be a string"):
        normalize_text(123)  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="`custom_map` must map strings to strings"):
        map_slang("texto", custom_map={"vc": 1})  # type: ignore[dict-item]


def test_cpp_acceleration_available_returns_bool() -> None:
    """The capability predicate reflects whether the backend is loaded."""
    from portunlp import cpp_acceleration_available

    assert isinstance(cpp_acceleration_available(), bool)
    assert cpp_acceleration_available() is (text_module._CPP_BACKEND is not None)


def test_tokenize_text_lowercases_accented_portuguese() -> None:
    """Tokenization lowercases accented letters via either backend."""
    assert tokenize_text("Olá MUNDO Coração") == ["olá", "mundo", "coração"]
    assert tokenize_text("ÀÇÃO São João") == ["àção", "são", "joão"]


def test_cpp_backend_is_optional() -> None:
    """The compiled backend is optional and either absent or a usable module."""
    backend = text_module._CPP_BACKEND
    if backend is None:
        pytest.skip("compiled C++ backend not available in this environment")
    # When present, it must expose the accelerated helpers used by text.py.
    assert backend.split_words("um dois") == ["um", "dois"]
    assert dict(backend.count_term_frequencies(["a", "a", "b"])) == {"a": 2, "b": 1}
    assert [list(ngram) for ngram in backend.build_ngrams(["a", "b", "c"], 2)] == [
        ["a", "b"],
        ["b", "c"],
    ]


@pytest.mark.parametrize(
    "text",
    [
        "Olá Mundo! Tudo BEM?",
        "Coração, ÇÃO, àÀ êÊ õÕ úÚ.",
        "São Paulo é ótimo; não é?",
        "MAIÚSCULAS e minúsculas 123 números",
        "Ele disse «olá» — e partiu até logo.",
        "a×b e c÷d não são palavras",
    ],
)
def test_cpp_tokenizer_matches_pure_python(text: str) -> None:
    """The native tokenizer is byte-for-byte equivalent to the Python path."""
    backend = text_module._CPP_BACKEND
    if backend is None:
        pytest.skip("compiled C++ backend not available in this environment")
    expected = text_module._iter_word_tokens(text)
    # Public API must agree regardless of which path the guard selects.
    assert tokenize_text(text) == expected
    # Where the guard routes to C++, the backend output must match exactly.
    if text_module._can_use_cpp_text(text):
        assert list(backend.split_words(text)) == expected
