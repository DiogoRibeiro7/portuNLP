test_that("tokenize_cpp splits words", {
  res_cpp <- tokenize_cpp("O gato dorme")[[1]]
  expect_equal(res_cpp, c("o", "gato", "dorme"))
})

test_that("tokenize_cpp handles punctuation", {
  res <- tokenize_cpp("Olá, mundo!")[[1]]
  expect_equal(res, c("olá", "mundo"))
})

test_that("tokenize_cpp splits contractions", {
  res <- tokenize_cpp("d'água")[[1]]
  expect_equal(res, c("d", "água"))
})
