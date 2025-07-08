#' Normalize Portuguese text
#'
#' This function applies basic normalization steps to Portuguese text, such as
#' converting to lower case, removing punctuation, and folding accents using
#' `stringi` utilities.
#'
#' @param text Character vector with input text.
#' @param lower Logical indicating whether to convert to lower case. Defaults to
#'   `TRUE`.
#' @param remove_punct Logical indicating whether to remove punctuation. Defaults
#'   to `FALSE`.
#' @param correct Logical indicating whether to apply built-in orthographic
#'   rules before accent normalization.
#'
#' @return A character vector with normalized text.
#' @examples
#' normalize_text("acção", correct = TRUE)
#'
#' @export
normalize_text <- function(text, lower = TRUE, remove_punct = FALSE,
                           correct = FALSE) {
  if (!is.character(text)) {
    stop("`text` must be a character vector")
  }
  result <- text
  # Convert to lower case if requested
  if (isTRUE(lower)) {
    result <- tolower(result)
  }
  # Remove punctuation if requested
  if (isTRUE(remove_punct)) {
    result <- gsub('[[:punct:]]+', '', result)
  }
  # Apply orthographic rules before accent folding
  if (isTRUE(correct)) {
    result <- apply_orth_rules(result)
  }

  # Normalize accents using stringi
  result <- stringi::stri_trans_general(result, 'Latin-ASCII')
  return(result)
}
