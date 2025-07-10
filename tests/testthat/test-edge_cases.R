test_that("functions handle empty input", {
  expect_equal(normalize_text(""), "")
  expect_equal(tokenize_pt("", type = "word")[[1]], character(0))
  expect_equal(apply_orth_rules(""), "")
  expect_equal(remove_emoji(""), "")
  expect_equal(map_slang(""), "")
  expect_equal(clean_social(""), "")
})
