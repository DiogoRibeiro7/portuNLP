# portuNLP

![R-CMD-check](https://github.com/DiogoRibeiro7/portuNLP/actions/workflows/R-CMD-check.yaml/badge.svg)

`portuNLP` is an R package for Portuguese text processing with a small Python
helper used for spaCy integration. **Python 3.10+ is required.** The toolkit currently includes:

- Text normalization via `normalize_text()`
- Tokenization with `tokenize_pt()`
- Optional C++ tokenizer built with CMake (`split_words()`), accessible in R via `tokenize_cpp()`
- Lemmatization and POS tagging using spaCy (`lemmatize_pt()`, `pos_tag_pt()`)
- Portuguese stopword handling through `get_stopwords()`
- Loading custom dictionaries using `load_dict()`
- Spell correction with `apply_orth_rules()` using the `orth_rules` dataset
- Social-media cleaning helpers: `remove_emoji()`, `normalize_accents()`,
  `map_slang()`, and the combined `clean_social()`
- POS tag mapping with `map_pos_tags()` or `pos_tag_pt(universal = TRUE)`
- Sample datasets such as `orth_rules`, `slang_map`, `stopwords_pt`, and `pos_map` accessible via `data(orth_rules)`, `data(slang_map)`, or `data(stopwords_pt)`
  The stopword list is adapted from the NLTK Portuguese collection, while the
  slang mapping reflects common abbreviations found in Brazilian social media.

Example using the C++ tokenizer:

```R
tokenize_cpp("O gato dorme")
```

## Installation

Ensure [Poetry](https://python-poetry.org/) is available and Python 3.10 or newer is installed, then run:

```bash
./setup.sh
```

The script installs R (and development headers) plus a minimal TeX
distribution if they are missing. It also installs the R packages
`stringi`, `reticulate`, and `testthat` via the system package manager and
installs Python dependencies with Poetry.

## Usage

```R
library(portuNLP)

normalize_text("Olá, Mundo!")
normalize_text("acção", correct = TRUE)
tokenize_pt("Gosto de R e Python.")
tokenize_spacy_pt("Gosto de R e Python.")
lemmatize_pt(c("gatos", "bonitos"))
pos_tag_pt(c("gatos", "bonitos"), universal = TRUE)
get_stopwords()
clean_social("vc tá 😊", custom_map = c(tá = "está"))
#> "voce esta "
apply_orth_rules("acto", orth_rules)
map_pos_tags(c("NOUN", "VERB"))
```

The accompanying Python module exposes helpers for tokenization,
lemmatization, and part-of-speech tagging using spaCy.  When the
`pt_core_news_sm` model is installed, `tokenize_spacy_pt()`,
`lemmatize_pt()`, and `pos_tag_pt()` transparently call these helpers via
`reticulate`.

## Development

After modifying the code, run the following checks:

```bash
R CMD check .
poetry run pytest
pre-commit run --all-files
mkdir -p build && cd build
cmake ..
make
ctest --output-on-failure
```

Continuous integration tests run automatically when changes are merged to the
`main` branch.

See `ROADMAP.md` for future plans and ongoing development stages.

Additional examples are available in the `vignettes/` directory. After
installing the package you can browse them with:

```R
browseVignettes("portuNLP")
```

If `pkgdown` is installed, you can build the documentation website with:

```R
pkgdown::build_site()
```

## Benchmarks

The script `benchmarks/benchmark_tokenize.R` provides a
`benchmark_tokenize()` helper that reports microbenchmark statistics and
the median tokenization throughput. Run it with:

```R
source("benchmarks/benchmark_tokenize.R")
benchmark_tokenize(rep("O elétrico está em ação.", 1000))
```
