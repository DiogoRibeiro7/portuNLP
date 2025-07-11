test_that("functions handle empty input", {
  expect_equal(normalize_text(""), "")
  expect_equal(tokenize_pt("", type = "word")[[1]], character(0))
  expect_equal(apply_orth_rules(""), "")
  expect_equal(remove_emoji(""), "")
  expect_equal(map_slang(""), "")
  expect_equal(clean_social(""), "")
})

test_that("normalize_text handles non-UTF8 input", {
  latin1 <- iconv("ação", from = "UTF-8", to = "latin1")
  res <- normalize_text(latin1)
  expect_equal(res, "acao")
})
