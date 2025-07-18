context("non-UTF8 input")

latin_text <- iconv("O elétrico está em ação.", from = "UTF-8", to = "latin1")
Encoding(latin_text) <- "latin1"

expect_equal(
  normalize_text(latin_text),
  normalize_text("O elétrico está em ação.")
)

expect_equal(
  tokenize_pt(latin_text, type = "word")[[1]],
  tokenize_pt("O elétrico está em ação.", type = "word")[[1]]
)

