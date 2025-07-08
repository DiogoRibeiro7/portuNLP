test_that("get_stopwords returns a character vector", {
  sw <- get_stopwords()
  expect_true(is.character(sw))
  expect_true("a" %in% sw)
})
