"""Command-line interface for high-level Portuguese NLP analysis."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Sequence

from .api import analysis_to_json, analyze_text, analyze_texts


def _add_common_arguments(parser: argparse.ArgumentParser) -> None:
    """Register arguments shared by text and corpus commands.

    Args:
        parser (argparse.ArgumentParser): Parser to configure.
    """
    parser.add_argument("--correct", action="store_true", help="Apply orthographic corrections.")
    parser.add_argument("--keep-punct", action="store_true", help="Keep punctuation during normalization.")
    parser.add_argument("--social", action="store_true", help="Apply social-text cleaning before normalization.")
    parser.add_argument("--remove-stopwords", action="store_true", help="Remove stopwords from token sequences.")
    parser.add_argument("--use-spacy", action="store_true", help="Use spaCy tokenization in preprocessing.")
    parser.add_argument("--include-spacy", action="store_true", help="Include structured spaCy analysis output.")
    parser.add_argument(
        "--include-spacy-lexicon",
        action="store_true",
        help="Include spaCy lexical summaries.",
    )
    parser.add_argument(
        "--include-spacy-collocations",
        action="store_true",
        help="Include spaCy collocation summaries.",
    )
    parser.add_argument(
        "--collocation-size",
        type=int,
        default=2,
        help="Collocation size when spaCy collocation summaries are enabled.",
    )
    parser.add_argument("--compact", action="store_true", help="Emit compact single-line JSON.")
    parser.add_argument("--output-file", help="Write JSON output to a file instead of stdout.")


def _resolve_text_input(text: str | None, input_file: str | None) -> str:
    """Resolve single-text input from an argument or a file.

    Args:
        text (str | None): Inline text argument.
        input_file (str | None): Optional input file path.

    Returns:
        str: Resolved input text.

    Raises:
        ValueError: If neither or both input sources are provided.
    """
    if bool(text) == bool(input_file):
        raise ValueError("Provide exactly one of `text` or `--input-file`")
    if input_file is not None:
        return Path(input_file).read_text(encoding="utf-8")
    return text or ""


def _resolve_texts_input(texts: list[str], input_file: str | None) -> list[str]:
    """Resolve corpus input from arguments or a file.

    Args:
        texts (list[str]): Inline text arguments.
        input_file (str | None): Optional newline-delimited input file path.

    Returns:
        list[str]: Resolved corpus texts.

    Raises:
        ValueError: If neither or both input sources are provided.
    """
    if bool(texts) == bool(input_file):
        raise ValueError("Provide exactly one of `texts` or `--input-file`")
    if input_file is not None:
        lines = Path(input_file).read_text(encoding="utf-8").splitlines()
        return [line for line in lines if line.strip()]
    return texts


def _emit_output(payload: str, output_file: str | None) -> None:
    """Write CLI output to stdout or a file.

    Args:
        payload (str): Serialized JSON payload.
        output_file (str | None): Optional output file path.
    """
    if output_file is not None:
        Path(output_file).write_text(payload + "\n", encoding="utf-8")
        return
    print(payload)


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI argument parser.

    Returns:
        argparse.ArgumentParser: Configured argument parser.
    """
    parser = argparse.ArgumentParser(prog="portunlp", description="Portuguese NLP analysis CLI.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    text_parser = subparsers.add_parser("text", help="Analyze a single text.")
    text_parser.add_argument("text", nargs="?", help="Text to analyze.")
    text_parser.add_argument("--input-file", help="Read the text to analyze from a UTF-8 file.")
    text_parser.add_argument("--keyword-top-k", type=int, default=10, help="Maximum number of keywords to return.")
    _add_common_arguments(text_parser)

    texts_parser = subparsers.add_parser("texts", help="Analyze multiple texts.")
    texts_parser.add_argument("texts", nargs="*", help="Texts to analyze.")
    texts_parser.add_argument(
        "--input-file",
        help="Read texts from a UTF-8 file with one text per line.",
    )
    texts_parser.add_argument("--ngram-size", type=int, default=2, help="N-gram size for aggregate statistics.")
    _add_common_arguments(texts_parser)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the CLI entry point.

    Args:
        argv (Sequence[str] | None): Optional command-line arguments.

    Returns:
        int: Process exit status.
    """
    parser = build_parser()
    args = parser.parse_args(argv)
    indent = None if args.compact else 2

    if args.command == "text":
        resolved_text = _resolve_text_input(args.text, args.input_file)
        text_result = analyze_text(
            resolved_text,
            correct=args.correct,
            remove_punct=not args.keep_punct,
            social=args.social,
            remove_stopwords=args.remove_stopwords,
            use_spacy=args.use_spacy,
            keyword_top_k=args.keyword_top_k,
            include_spacy=args.include_spacy,
            include_spacy_lexicon=args.include_spacy_lexicon,
            include_spacy_collocations=args.include_spacy_collocations,
            collocation_size=args.collocation_size,
        )
        _emit_output(analysis_to_json(text_result, indent=indent), args.output_file)
        return 0

    if args.command == "texts":
        resolved_texts = _resolve_texts_input(args.texts, args.input_file)
        corpus_result = analyze_texts(
            resolved_texts,
            correct=args.correct,
            remove_punct=not args.keep_punct,
            social=args.social,
            remove_stopwords=args.remove_stopwords,
            use_spacy=args.use_spacy,
            ngram_size=args.ngram_size,
            include_spacy=args.include_spacy,
            include_spacy_lexicon=args.include_spacy_lexicon,
            include_spacy_collocations=args.include_spacy_collocations,
            collocation_size=args.collocation_size,
        )
        _emit_output(analysis_to_json(corpus_result, indent=indent), args.output_file)
        return 0

    parser.error(f"Unsupported command: {args.command}")
    return 2
