import sys
import types

# Provide a minimal spaCy stub if spaCy is unavailable
if "spacy" not in sys.modules:
    fake = types.ModuleType("spacy")
    fake.__fake__ = True  # type: ignore[attr-defined]

    def load(name: str):
        raise ModuleNotFoundError("spaCy not installed")

    fake.load = load  # type: ignore[attr-defined]
    sys.modules["spacy"] = fake
