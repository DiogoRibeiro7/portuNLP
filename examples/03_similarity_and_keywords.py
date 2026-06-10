"""Keyword extraction and document similarity.

Run with::

    python examples/03_similarity_and_keywords.py
"""

from portunlp import compare_texts, extract_keywords, rank_similar_texts


def main() -> None:
    """Extract keywords and rank documents by similarity."""
    document = (
        "O clima da cidade mudou muito: o verão ficou mais quente e seco, "
        "enquanto o inverno trouxe chuvas intensas."
    )
    print("== keywords ==")
    for keyword in extract_keywords(document, top_k=6, remove_stopwords=True):
        print(f"  {keyword.token:<12} {keyword.score:.4f}")

    corpus = [
        "O verão está cada vez mais quente nas grandes cidades.",
        "A receita leva farinha, ovos e açúcar.",
        "As chuvas de inverno causaram enchentes na região.",
    ]
    query = "ondas de calor e clima quente no verão"

    print("\n== similarity to query ==")
    print(f"query: {query!r}")
    for match in rank_similar_texts(query, corpus, top_k=3):
        print(f"  [{match.score:.3f}] {match.text}")

    print("\n== pairwise ==")
    print(f"  {compare_texts(corpus[0], query):.3f} (verão vs query)")
    print(f"  {compare_texts(corpus[1], query):.3f} (receita vs query)")


if __name__ == "__main__":
    main()
