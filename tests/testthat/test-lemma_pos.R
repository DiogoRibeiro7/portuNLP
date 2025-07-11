library(testthat)

skip_if_not(reticulate::py_module_available("portunlp"))
skip_if_not(reticulate::py_module_available("spacy"))
skip_if_not(reticulate::py_eval("__import__('spacy').util.is_package('pt_core_news_sm')"),
           message = "spaCy Portuguese model missing")

test_that("lemmatize_pt uses spaCy", {
  lemmas <- lemmatize_pt(c("gatos", "bonitos"))
  expect_true(is.character(lemmas))
  expect_true(length(lemmas) >= 2)
})

test_that("pos_tag_pt uses spaCy", {
  tags <- pos_tag_pt(c("O", "gato", "dorme"), universal = TRUE)
  expect_true(is.character(tags))
  expect_equal(length(tags), 3)
})
