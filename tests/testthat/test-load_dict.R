test_that("load_dict reads words", {
  path <- system.file("extdata", "sample_dict.txt", package = "portuNLP")
  words <- load_dict(path)
  expect_true(is.character(words))
  expect_true("ação" %in% words)
})

test_that("load_dict errors on missing file", {
  expect_error(load_dict("nonexistent.txt"), "File not found")
})
