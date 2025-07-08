library(testthat)

skip_if_not(reticulate::py_module_available("portunlp"))

test_that("tokenize_spacy_pt calls Python helper", {
  toks <- tokenize_spacy_pt("Olá mundo")
  expect_true(is.list(toks))
  expect_true(length(toks[[1]]) >= 2)
})
