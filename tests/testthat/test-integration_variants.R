test_that("tokenization consistent across variants", {
  eu <- "O electrico está em acção."
  br <- "O elétrico está em ação."
  toks_eu <- tokenize_pt(apply_orth_rules(eu), type = "word")[[1]]
  toks_br <- tokenize_pt(br, type = "word")[[1]]
  expect_equal(toks_eu, toks_br)
})

test_that("sentence tokenization yields same result", {
  eu <- "O electrico está em acção. Dois factos curiosos."
  br <- "O elétrico está em ação. Dois fatos curiosos."
  sen_eu <- tokenize_pt(apply_orth_rules(eu), type = "sentence")[[1]]
  sen_br <- tokenize_pt(br, type = "sentence")[[1]]
  expect_equal(sen_eu, sen_br)
})

test_that("normalize_text aligns variants", {
  eu <- "O electrico está em acção! Dois factos?"
  br <- "O elétrico está em ação! Dois fatos?"
  norm_eu <- normalize_text(eu, remove_punct = TRUE, correct = TRUE)
  norm_br <- normalize_text(br, remove_punct = TRUE)
  expect_equal(norm_eu, norm_br)
})

test_that("clean_social produces identical tokens", {
  eu <- "Tb gosto do electrico 😊"
  br <- "Tb gosto do elétrico 😊"
  cleaned_eu <- clean_social(apply_orth_rules(eu), custom_map = c(tb = "também"))
  cleaned_br <- clean_social(br, custom_map = c(tb = "também"))
  toks_eu <- tokenize_pt(cleaned_eu, type = "word")[[1]]
  toks_br <- tokenize_pt(cleaned_br, type = "word")[[1]]
  expect_equal(toks_eu, toks_br)
})

# Only run lemmatization and POS tagging when Python helpers are available
skip_if_not(reticulate::py_module_available("portunlp"))

test_that("lemmas and tags match across variants", {
  eu <- "O electrico está em acção."
  br <- "O elétrico está em ação."
  toks_eu <- tokenize_pt(apply_orth_rules(eu), type = "word")[[1]]
  toks_br <- tokenize_pt(br, type = "word")[[1]]
  lem_eu <- lemmatize_pt(toks_eu)
  lem_br <- lemmatize_pt(toks_br)
  expect_equal(lem_eu, lem_br)
  tags_eu <- pos_tag_pt(toks_eu, universal = TRUE)
  tags_br <- pos_tag_pt(toks_br, universal = TRUE)
  expect_equal(tags_eu, tags_br)
})
