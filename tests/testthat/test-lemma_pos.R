library(testthat)

skip_if_not(reticulate::py_module_available("portunlp"))

test_that("lemmatize_pt uses spaCy", {
  lemmas <- lemmatize_pt(c("gatos", "bonitos"))
  expect_true(is.character(lemmas))
  expect_true(length(lemmas) >= 2)
})

test_that("pos_tag_pt uses spaCy", {
  tags <- pos_tag_pt(c("O", "gato", "dorme"))
  expect_true(is.character(tags))
  expect_equal(length(tags), 3)
})
