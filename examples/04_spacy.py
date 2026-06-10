"""spaCy-backed analysis (requires the pt_core_news_sm model).

Install the model first::

    python -m spacy download pt_core_news_sm

Run with::

    python examples/04_spacy.py
"""

from portunlp import spacy_entities, spacy_morphology, spacy_to_json


def main() -> int:
    """Run a few spaCy-backed helpers, skipping cleanly if the model is absent."""
    text = "O presidente Lula visitou o Porto em janeiro de 2024."
    try:
        morphology = spacy_morphology(text)
        entities = spacy_entities(text)
    except OSError as error:
        print("spaCy model not available:", error)
        print("Install it with: python -m spacy download pt_core_news_sm")
        return 1

    print("== morphology (first 5 tokens) ==")
    for token in morphology.tokens[:5]:
        print(f"  {token.text:<12} {token.pos:<6} {token.lemma}")

    print("\n== entities ==")
    for entity in entities.entities:
        print(f"  {entity.text:<20} {entity.label}")

    print("\n== entities as JSON ==")
    print(spacy_to_json(entities))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
