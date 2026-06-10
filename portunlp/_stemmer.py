"""Portuguese stemmer implementing the Snowball (Porter2) algorithm.

This is a clean-room reimplementation of the published Portuguese stemming
algorithm (https://snowballstem.org/algorithms/portuguese/stemmer.html). Its
output matches NLTK's ``SnowballStemmer("portuguese")`` (with the default
``ignore_stopwords=False``). The suffix tables and step ordering are part of the
algorithm specification.
"""

from __future__ import annotations

_VOWELS = "aeiou\xe1\xe9\xed\xf3\xfa\xe2\xea\xf4"

_STEP1_SUFFIXES = (
    "amentos",
    "imentos",
    "u\xe7o~es",
    "amento",
    "imento",
    "adoras",
    "adores",
    "a\xe7o~es",
    "logias",
    "\xeancias",
    "amente",
    "idades",
    "an\xe7as",
    "ismos",
    "istas",
    "adora",
    "a\xe7a~o",
    "antes",
    "\xe2ncia",
    "logia",
    "u\xe7a~o",
    "\xeancia",
    "mente",
    "idade",
    "an\xe7a",
    "ezas",
    "icos",
    "icas",
    "ismo",
    "\xe1vel",
    "\xedvel",
    "ista",
    "osos",
    "osas",
    "ador",
    "ante",
    "ivas",
    "ivos",
    "iras",
    "eza",
    "ico",
    "ica",
    "oso",
    "osa",
    "iva",
    "ivo",
    "ira",
)

_STEP2_SUFFIXES = (
    "ar\xedamos",
    "er\xedamos",
    "ir\xedamos",
    "\xe1ssemos",
    "\xeassemos",
    "\xedssemos",
    "ar\xedeis",
    "er\xedeis",
    "ir\xedeis",
    "\xe1sseis",
    "\xe9sseis",
    "\xedsseis",
    "\xe1ramos",
    "\xe9ramos",
    "\xedramos",
    "\xe1vamos",
    "aremos",
    "eremos",
    "iremos",
    "ariam",
    "eriam",
    "iriam",
    "assem",
    "essem",
    "issem",
    "ara~o",
    "era~o",
    "ira~o",
    "arias",
    "erias",
    "irias",
    "ardes",
    "erdes",
    "irdes",
    "asses",
    "esses",
    "isses",
    "astes",
    "estes",
    "istes",
    "\xe1reis",
    "areis",
    "\xe9reis",
    "ereis",
    "\xedreis",
    "ireis",
    "\xe1veis",
    "\xedamos",
    "armos",
    "ermos",
    "irmos",
    "aria",
    "eria",
    "iria",
    "asse",
    "esse",
    "isse",
    "aste",
    "este",
    "iste",
    "arei",
    "erei",
    "irei",
    "aram",
    "eram",
    "iram",
    "avam",
    "arem",
    "erem",
    "irem",
    "ando",
    "endo",
    "indo",
    "adas",
    "idas",
    "ar\xe1s",
    "aras",
    "er\xe1s",
    "eras",
    "ir\xe1s",
    "avas",
    "ares",
    "eres",
    "ires",
    "\xedeis",
    "ados",
    "idos",
    "\xe1mos",
    "amos",
    "emos",
    "imos",
    "iras",
    "ada",
    "ida",
    "ar\xe1",
    "ara",
    "er\xe1",
    "era",
    "ir\xe1",
    "ava",
    "iam",
    "ado",
    "ido",
    "ias",
    "ais",
    "eis",
    "ira",
    "ia",
    "ei",
    "am",
    "em",
    "ar",
    "er",
    "ir",
    "as",
    "es",
    "is",
    "eu",
    "iu",
    "ou",
)

_STEP4_SUFFIXES = ("os", "a", "i", "o", "\xe1", "\xed", "\xf3")


def _r1r2(word: str) -> tuple[str, str]:
    """Return the R1 and R2 string regions for ``word``.

    Args:
        word (str): Word with tilde placeholders applied.

    Returns:
        tuple[str, str]: The R1 and R2 regions as suffix substrings.
    """
    r1 = ""
    r2 = ""
    for i in range(1, len(word)):
        if word[i] not in _VOWELS and word[i - 1] in _VOWELS:
            r1 = word[i + 1 :]
            break
    for i in range(1, len(r1)):
        if r1[i] not in _VOWELS and r1[i - 1] in _VOWELS:
            r2 = r1[i + 1 :]
            break
    return r1, r2


def _rv(word: str) -> str:
    """Return the RV string region for ``word``.

    Args:
        word (str): Word with tilde placeholders applied.

    Returns:
        str: The RV region as a suffix substring.
    """
    if len(word) < 2:
        return ""
    if word[1] not in _VOWELS:
        for i in range(2, len(word)):
            if word[i] in _VOWELS:
                return word[i + 1 :]
        return ""
    if word[0] in _VOWELS and word[1] in _VOWELS:
        for i in range(2, len(word)):
            if word[i] not in _VOWELS:
                return word[i + 1 :]
        return ""
    return word[3:]


def snowball_stem(word: str) -> str:
    """Stem a single lowercase Portuguese word with the Snowball algorithm.

    Args:
        word (str): Input word (any case).

    Returns:
        str: The stemmed form.
    """
    word = word.lower()
    word = (
        word.replace("\xe3", "a~")
        .replace("\xf5", "o~")
        .replace("q\xfc", "qu")
        .replace("g\xfc", "gu")
    )

    r1, r2 = _r1r2(word)
    rv = _rv(word)

    step1_success = False
    step2_success = False

    # STEP 1: standard suffix removal.
    for suffix in _STEP1_SUFFIXES:
        if not word.endswith(suffix):
            continue
        if suffix == "amente" and r1.endswith(suffix):
            step1_success = True
            word = word[:-6]
            r2 = r2[:-6]
            rv = rv[:-6]
            if r2.endswith("iv"):
                word = word[:-2]
                r2 = r2[:-2]
                rv = rv[:-2]
                if r2.endswith("at"):
                    word = word[:-2]
                    rv = rv[:-2]
            elif r2.endswith(("os", "ic", "ad")):
                word = word[:-2]
                rv = rv[:-2]
        elif (
            suffix in ("ira", "iras")
            and rv.endswith(suffix)
            and word[-len(suffix) - 1 : -len(suffix)] == "e"
        ):
            step1_success = True
            word = word[: -len(suffix)] + "ir"
            rv = rv[: -len(suffix)] + "ir"
        elif r2.endswith(suffix):
            step1_success = True
            if suffix in ("logia", "logias"):
                word = word[: -len(suffix)] + "log"
                rv = rv[: -len(suffix)] + "log"
            elif suffix in ("u\xe7a~o", "u\xe7o~es"):
                word = word[: -len(suffix)] + "u"
                rv = rv[: -len(suffix)] + "u"
            elif suffix in ("\xeancia", "\xeancias"):
                word = word[: -len(suffix)] + "ente"
                rv = rv[: -len(suffix)] + "ente"
            elif suffix == "mente":
                word = word[:-5]
                r2 = r2[:-5]
                rv = rv[:-5]
                if r2.endswith(("ante", "avel", "ivel")):
                    word = word[:-4]
                    rv = rv[:-4]
            elif suffix in ("idade", "idades"):
                word = word[: -len(suffix)]
                r2 = r2[: -len(suffix)]
                rv = rv[: -len(suffix)]
                if r2.endswith(("ic", "iv")):
                    word = word[:-2]
                    rv = rv[:-2]
                elif r2.endswith("abil"):
                    word = word[:-4]
                    rv = rv[:-4]
            elif suffix in ("iva", "ivo", "ivas", "ivos"):
                word = word[: -len(suffix)]
                r2 = r2[: -len(suffix)]
                rv = rv[: -len(suffix)]
                if r2.endswith("at"):
                    word = word[:-2]
                    rv = rv[:-2]
            else:
                word = word[: -len(suffix)]
                rv = rv[: -len(suffix)]
        break

    # STEP 2: verb suffixes.
    if not step1_success:
        for suffix in _STEP2_SUFFIXES:
            if rv.endswith(suffix):
                step2_success = True
                word = word[: -len(suffix)]
                rv = rv[: -len(suffix)]
                break

    # STEP 3.
    if step1_success or step2_success:
        if rv.endswith("i") and word[-2:-1] == "c":
            word = word[:-1]
            rv = rv[:-1]

    # STEP 4: residual suffix.
    if not step1_success and not step2_success:
        for suffix in _STEP4_SUFFIXES:
            if rv.endswith(suffix):
                word = word[: -len(suffix)]
                rv = rv[: -len(suffix)]
                break

    # STEP 5.
    if rv.endswith(("e", "\xe9", "\xea")):
        word = word[:-1]
        rv = rv[:-1]
        if (word.endswith("gu") and rv.endswith("u")) or (
            word.endswith("ci") and rv.endswith("i")
        ):
            word = word[:-1]
    elif word.endswith("\xe7"):
        word = word[:-1] + "c"

    return word.replace("a~", "\xe3").replace("o~", "\xf5")
