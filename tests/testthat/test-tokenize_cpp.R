test_that("tokenize_cpp splits words", {
  res_cpp <- tokenize_cpp("O gato dorme")[[1]]
  expect_equal(res_cpp, c("O", "gato", "dorme"))
})
