test_that("get_stopwords returns expanded list", {
  sw <- get_stopwords()
  expect_true(is.character(sw))
  expect_gte(length(sw), 40)
  expect_true("não" %in% sw)
})

test_that("stopwords dataset is available", {
  data(stopwords_pt)
  expect_true(is.character(stopwords_pt))
  expect_gte(length(stopwords_pt), 40)
})
