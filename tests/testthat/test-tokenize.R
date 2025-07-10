test_that("tokenize_pt splits sentences", {
  toks <- tokenize_pt("Olá mundo! Tudo bem?", type = "word")
  expect_true(is.list(toks))
  expect_true(length(toks[[1]]) >= 2)
})


 test_that("tokenize_pt sentences", {
   toks <- tokenize_pt("Ola. Tudo bem?", type = "sentence")
   expect_equal(length(toks[[1]]), 2)
 })

 test_that("tokenize_pt errors on non-character", {
   expect_error(tokenize_pt(123), "`text` must be a character")
 })
