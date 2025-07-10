# Skip if Python helper is available
skip_if(reticulate::py_module_available("portunlp"))

test_that("lemmatize_pt falls back when Python missing", {
  tokens <- c("gatos", "bonitos")
  lemmas <- lemmatize_pt(tokens)
  expect_equal(lemmas, tokens)
})

test_that("pos_tag_pt falls back when Python missing", {
  tokens <- c("O", "gato")
  tags <- pos_tag_pt(tokens)
  expect_equal(tags, rep("UNK", length(tokens)))
})
