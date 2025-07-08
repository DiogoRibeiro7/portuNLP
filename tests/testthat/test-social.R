test_that("remove_emoji strips pictographs", {
  expect_equal(remove_emoji("ola 😊"), "ola ")
})

test_that("normalize_accents folds characters", {
  expect_equal(normalize_accents("ação"), "acao")
})

test_that("map_slang replaces words", {
  expect_equal(map_slang("tbm gosto"), "também gosto")
})

test_that("clean_social combines steps", {
  res <- clean_social("vc tá 😊", custom_map = c(tá = "está"))
  expect_equal(res, "voce esta ")
})
