"""Native preprocessing helpers: normalize, slang, contractions, tokens.

Run with::

    python examples/02_preprocessing.py
"""

from portunlp import (
    clean_social_text,
    cpp_acceleration_available,
    expand_contractions,
    filter_stopwords,
    generate_ngrams,
    map_slang,
    normalize_text,
    tokenize_text,
)


def main() -> None:
    """Demonstrate the pure-Python preprocessing helpers."""
    print(f"C++ acceleration available: {cpp_acceleration_available()}\n")

    raw = "Vc viu o gato?? Tá na casa da Maria! 😻"
    print("raw            :", raw)
    print("slang          :", map_slang(raw))
    print("social-cleaned :", clean_social_text(raw))
    print("normalized     :", normalize_text(raw, remove_punct=True))

    sentence = "Fui ao mercado do bairro e falei pelos cotovelos."
    print("\ncontractions in:", sentence)
    print("contractions out:", expand_contractions(sentence))

    tokens = tokenize_text("São Paulo é uma cidade grande e bonita.")
    print("\ntokens         :", tokens)
    print("no stopwords   :", filter_stopwords(tokens, normalize=True))
    print("bigrams        :", generate_ngrams(tokens, 2)[:4])


if __name__ == "__main__":
    main()
