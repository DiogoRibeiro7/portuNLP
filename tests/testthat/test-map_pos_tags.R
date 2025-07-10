test_that("map_pos_tags converts known tags", {
  data(pos_map)
  universal <- map_pos_tags(c("NOUN", "VERB"))
  expect_equal(universal, c("NOUN", "VERB"))
})

test_that("map_pos_tags leaves unknown tags", {
  res <- map_pos_tags(c("UNKNOWN"))
  expect_equal(res, c("UNKNOWN"))
})
