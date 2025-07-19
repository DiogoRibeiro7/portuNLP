library(testthat)

skip_if_not(reticulate::py_module_available("portunlp"))
skip_if_not(reticulate::py_module_available("spacy"))
skip_if_not(reticulate::py_eval("__import__('spacy').util.is_package('pt_core_news_sm')"),
           message = "spaCy Portuguese model missing")

test_that("tokenize_spacy_pt calls Python helper", {
  toks <- tokenize_spacy_pt("Olá mundo")
  expect_true(is.list(toks))
  expect_true(length(toks[[1]]) >= 2)
})
