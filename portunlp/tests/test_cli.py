import json
from pathlib import Path

import pytest

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


def test_cli_text_can_read_from_file(tmp_path: Path, capsys) -> None:
    """The text subcommand can read its input from a file."""
    input_path = tmp_path / "input.txt"
    input_path.write_text("A casa bonita", encoding="utf-8")

    exit_code = main(["text", "--input-file", str(input_path), "--compact"])
    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert exit_code == 0
    assert payload["text"] == "A casa bonita"


def test_cli_texts_can_read_from_file(tmp_path: Path, capsys) -> None:
    """The texts subcommand can read one text per line from a file."""
    input_path = tmp_path / "inputs.txt"
    input_path.write_text("A casa bonita\nA casa azul\n", encoding="utf-8")

    exit_code = main(["texts", "--input-file", str(input_path), "--remove-stopwords", "--compact"])
    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert exit_code == 0
    assert payload["texts"] == ["A casa bonita", "A casa azul"]


def test_cli_can_write_output_to_file(tmp_path: Path, capsys) -> None:
    """The CLI can write JSON output to a file instead of stdout."""
    output_path = tmp_path / "output.json"

    exit_code = main(["text", "A casa bonita", "--compact", "--output-file", str(output_path)])
    captured = capsys.readouterr()
    payload = json.loads(output_path.read_text(encoding="utf-8"))

    assert exit_code == 0
    assert captured.out == ""
    assert payload["text"] == "A casa bonita"


def test_cli_rejects_conflicting_text_inputs() -> None:
    """The text subcommand rejects mixed inline and file input."""
    with pytest.raises(ValueError, match="Provide exactly one of `text` or `--input-file`"):
        main(["text", "A casa bonita", "--input-file", "input.txt"])


def test_cli_rejects_missing_texts_input() -> None:
    """The texts subcommand rejects missing input sources."""
    with pytest.raises(ValueError, match="Provide exactly one of `texts` or `--input-file`"):
        main(["texts"])
