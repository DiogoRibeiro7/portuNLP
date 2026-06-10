"""Quickstart: the high-level analysis facade.

Run with::

    python examples/01_quickstart.py
"""

from portunlp import analyze_text, analyze_texts, analysis_to_json


def main() -> None:
    """Analyze a single text and a small corpus, printing JSON."""
    single = analyze_text(
        "Os gatos bonitos comem peixe no rio.",
        remove_stopwords=True,
        keyword_top_k=5,
    )
    print("== single text ==")
    print(f"tokens          : {single.processed.tokens}")
    print(f"filtered tokens : {single.processed.filtered_tokens}")
    print(f"sentence count  : {single.metrics.sentence_count}")
    print(f"lexical diversity: {single.metrics.lexical_diversity:.3f}")
    print(f"top keywords    : {[(k.token, round(k.score, 3)) for k in single.keywords]}")

    corpus = analyze_texts(
        ["A casa bonita e azul.", "A casa azul fica no campo."],
        remove_stopwords=True,
        ngram_size=2,
    )
    print("\n== corpus ==")
    print(f"documents : {corpus.statistics.document_count}")
    print(f"tokens    : {corpus.statistics.token_count}")
    print(f"top bigrams: {sorted(corpus.statistics.ngrams.items(), key=lambda kv: -kv[1])[:3]}")

    print("\n== JSON (single, truncated) ==")
    print(analysis_to_json(single)[:400] + " ...")


if __name__ == "__main__":
    main()
