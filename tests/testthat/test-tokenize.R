test_that("tokenize_pt splits sentences", {
  toks <- tokenize_pt("Olá mundo! Tudo bem?", type = "word")
  expect_true(is.list(toks))
  expect_true(length(toks[[1]]) >= 2)
})

