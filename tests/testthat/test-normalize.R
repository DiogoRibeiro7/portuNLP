test_that("normalize_text works", {
  expect_equal(normalize_text("Olá"), "ola")
  expect_equal(normalize_text("acto", correct = TRUE), "ato")
})

test_that("apply_orth_rules replaces variants", {
  expect_equal(apply_orth_rules("acção"), "ação")
  expect_equal(apply_orth_rules("electrico"), "elétrico")
})

test_that("normalize_text errors on non-character input", {
  expect_error(normalize_text(123), "`text` must be a character")
})

test_that("remove punctuation when requested", {
  expect_equal(normalize_text("Ola, mundo!", remove_punct = TRUE), "ola mundo")
})
