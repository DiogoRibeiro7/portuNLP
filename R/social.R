#' Remove emoji from text
#'
#' This helper removes any Unicode emoji characters using
#' `stringi`'s `stri_replace_all_regex` with the
#' `\p{Emoji}` property.
#'
#' @param text Character vector to clean.
#'
#' @return Character vector with emoji removed.
#' @examples
#' remove_emoji("Olá 😊")
#' @export
remove_emoji <- function(text) {
  if (!is.character(text)) {
    stop("`text` must be a character vector")
  }
  stringi::stri_replace_all_regex(text, "\\p{Emoji}", "", vectorize_all = FALSE)
}

#' Normalize accents in Portuguese text
#'
#' Converts accented characters to their ASCII equivalents using
#' `stringi::stri_trans_general`.
#'
#' @param text Character vector with input text.
#'
#' @return Character vector with accents normalized.
#' @examples
#' normalize_accents("ação")
#' @export
normalize_accents <- function(text) {
  if (!is.character(text)) {
    stop("`text` must be a character vector")
  }
  stringi::stri_trans_general(text, "Latin-ASCII")
}

#' Map Portuguese slang to standard forms
#'
#' Replaces occurrences of known slang terms with their standard
#' equivalents. A minimal built-in map is provided and can be
#' extended with `custom_map`.
#'
#' @param text Character vector with input text.
#' @param custom_map Optional named character vector where names are
#'   slang terms and values are replacements.
#'
#' @return Character vector with slang replaced.
#' @examples
#' map_slang("tbm gosto", custom_map = c(tbm = "também"))
#' @export
map_slang <- function(text, custom_map = NULL) {
  if (!is.character(text)) {
    stop("`text` must be a character vector")
  }
  map <- c(slang_map, custom_map)
  if (length(map) == 0) {
    return(text)
  }
  result <- text
  for (term in names(map)) {
    pattern <- paste0("\\b", term, "\\b")
    result <- gsub(pattern, map[[term]], result, ignore.case = TRUE)
  }
  result
}

#' Clean Portuguese social-media text
#'
#' Applies several cleaning steps in the following order:
#' emoji removal, slang mapping, and accent normalization.
#'
#' @param text Character vector with input text.
#' @param emoji Logical; if `TRUE`, remove emoji.
#' @param accents Logical; if `TRUE`, normalize accents.
#' @param slang Logical; if `TRUE`, apply slang mapping.
#' @param custom_map Optional named vector for additional slang mappings.
#'
#' @return Character vector of cleaned text.
#' @examples
#' clean_social("Gosto mt disto 😊!", custom_map = c(mt = "muito"))
#' @export
clean_social <- function(text, emoji = TRUE, accents = TRUE, slang = TRUE,
                         custom_map = NULL) {
  if (!is.character(text)) {
    stop("`text` must be a character vector")
  }
  result <- text
  if (isTRUE(emoji)) {
    result <- remove_emoji(result)
  }
  if (isTRUE(slang)) {
    result <- map_slang(result, custom_map = custom_map)
  }
  if (isTRUE(accents)) {
    result <- normalize_accents(result)
  }
  result
}

#' Minimal slang mapping
#'
#' A small set of Portuguese slang words mapped to their standard forms.
#'
#' @format Named character vector where names are slang terms and
#'   values are replacements.
#' @source Manually curated for examples.
#' @examples
#' data(slang_map)
"slang_map"
