test_that("normalize_text works", {
  expect_equal(normalize_text("Olá"), "ola")
  expect_equal(normalize_text("acto", correct = TRUE), "ato")
})

test_that("apply_orth_rules replaces variants", {
  expect_equal(apply_orth_rules("acção"), "ação")
  expect_equal(apply_orth_rules("electrico"), "elétrico")
})
