test_that("pos_map data frame is available", {
  data(pos_map)
  expect_true(is.data.frame(pos_map))
  expect_true(all(c("spacy", "universal") %in% names(pos_map)))
})
