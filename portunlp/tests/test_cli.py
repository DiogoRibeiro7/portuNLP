import json

from portunlp.cli import main


def test_cli_text_outputs_json(capsys) -> None:
    """The text subcommand emits a serialized text analysis."""
    exit_code = main(["text", "A casa bonita", "--compact"])
    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert exit_code == 0
    assert payload["text"] == "A casa bonita"
    assert payload["processed"]["filtered_tokens"] == ["a", "casa", "bonita"]


def test_cli_text_honors_stopword_flag(capsys) -> None:
    """The text subcommand applies stopword removal when requested."""
    exit_code = main(["text", "A casa bonita", "--remove-stopwords", "--compact"])
    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert exit_code == 0
    assert payload["processed"]["filtered_tokens"] == ["casa", "bonita"]


def test_cli_texts_outputs_json(capsys) -> None:
    """The texts subcommand emits a serialized corpus analysis."""
    exit_code = main(["texts", "A casa bonita", "A casa azul", "--remove-stopwords", "--compact"])
    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert exit_code == 0
    assert payload["texts"] == ["A casa bonita", "A casa azul"]
    assert payload["statistics"]["frequencies"] == {"casa": 2, "bonita": 1, "azul": 1}


def test_cli_texts_honors_ngram_size(capsys) -> None:
    """The texts subcommand forwards the n-gram size option."""
    exit_code = main(
        ["texts", "A casa bonita", "A casa azul", "--remove-stopwords", "--ngram-size", "1", "--compact"]
    )
    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert exit_code == 0
    assert payload["statistics"]["ngrams"] == {"casa": 2, "bonita": 1, "azul": 1}
