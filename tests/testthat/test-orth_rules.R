test_that("orth_rules has expected size", {
  data(orth_rules)
  expect_true(is.data.frame(orth_rules))
  expect_gte(nrow(orth_rules), 5)
})
