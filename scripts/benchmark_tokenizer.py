"""Benchmark the native C++ acceleration against the pure-Python paths.

Run with the compiled backend available to compare throughput, e.g.::

    python scripts/benchmark_tokenizer.py
    python scripts/benchmark_tokenizer.py --tokens 2000000

On Windows, set ``PORTUNLP_DLL_DIRECTORIES`` to the directory holding the
backend's runtime DLLs if the extension fails to load.
"""

from __future__ import annotations

import argparse
import time
from typing import Callable

from portunlp.text import (
    _CPP_BACKEND,
    _iter_word_tokens,
    cpp_acceleration_available,
)


_SAMPLE = "Olá Mundo a casa bonita azul o gato come peixe no rio São João "


def _time(label: str, fn: Callable[[], object], *, repeat: int = 3) -> float:
    """Time ``fn`` and return the best wall-clock duration in seconds.

    Args:
        label (str): Display label.
        fn (Callable[[], object]): Zero-argument callable to time.
        repeat (int): Number of repetitions; the fastest is reported.

    Returns:
        float: Best observed duration in seconds.
    """
    best = float("inf")
    for _ in range(repeat):
        start = time.perf_counter()
        fn()
        best = min(best, time.perf_counter() - start)
    print(f"  {label:<28} {best * 1000:9.1f} ms")
    return best


def main() -> int:
    """Run the benchmark.

    Returns:
        int: Process exit status.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tokens", type=int, default=1_000_000, help="Approximate token count.")
    args = parser.parse_args()

    repetitions = max(1, args.tokens // len(_SAMPLE.split()))
    text = _SAMPLE * repetitions
    tokens = _iter_word_tokens(text)

    print(f"backend available: {cpp_acceleration_available()}")
    print(f"tokens: {len(tokens):,}\n")

    print("tokenize:")
    py_tok = _time("pure-python", lambda: _iter_word_tokens(text))
    if _CPP_BACKEND is not None:
        cpp_tok = _time("c++", lambda: _CPP_BACKEND.split_words(text))
        print(f"  speedup: {py_tok / cpp_tok:.1f}x\n")

    print("term frequencies:")
    py_tf = _time("pure-python (Counter)", lambda: __import__("collections").Counter(tokens))
    if _CPP_BACKEND is not None:
        cpp_tf = _time("c++", lambda: _CPP_BACKEND.count_term_frequencies(tokens))
        print(f"  speedup: {py_tf / cpp_tf:.1f}x\n")

    print("bigrams:")
    py_ng = _time(
        "pure-python",
        lambda: [tuple(tokens[i : i + 2]) for i in range(len(tokens) - 1)],
    )
    if _CPP_BACKEND is not None:
        cpp_ng = _time("c++", lambda: _CPP_BACKEND.build_ngrams(tokens, 2))
        print(f"  speedup: {py_ng / cpp_ng:.1f}x")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
