# Ensure no cleaning when all flags are FALSE
 test_that("clean_social no-op", {
   input <- "opa 😊"
   expect_equal(clean_social(input, emoji = FALSE, accents = FALSE, slang = FALSE), input)
 })

 test_that("clean_social removes only emoji", {
   input <- "opa 😊"
   expect_equal(clean_social(input, slang = FALSE, accents = FALSE), "opa ")
 })
