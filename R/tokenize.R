#' Tokenize Portuguese text
#'
#' Splits text into tokens using `stringi` boundary detection. This is a
#' simplistic tokenizer meant as a placeholder until integration with external
#' libraries (e.g., FreeLing or spaCy).
#'
#' @param text Character vector with input text.
#' @param type Boundary type: either "word" or "sentence". Defaults to "word".
#'
#' @return A list where each element is a character vector of tokens.
#' @examples
#' tokenize_pt("Olá mundo! Tudo bem?", type = "word")
#'
#' @export
tokenize_pt <- function(text, type = c("word", "sentence")) {
  if (!is.character(text)) {
    stop("`text` must be a character vector")
  }
  type <- match.arg(type)
  boundary <- if (type == "word") "word" else "sentence"
  tokens <- stringi::stri_split_boundaries(text, type = boundary, simplify = FALSE)
  return(tokens)
}

#' Tokenize Portuguese text with spaCy
#'
#' Calls the Python helper `portunlp.spacy_tokenize()` via `reticulate`.
#' Requires the spaCy Portuguese model `pt_core_news_sm` to be installed.
#'
#' @param text Character vector with input text.
#'
#' @return A list where each element is a character vector of tokens.
#' @examples
#' tokenize_spacy_pt("Olá mundo!")
#' @export
tokenize_spacy_pt <- function(text) {
  if (!is.character(text)) {
    stop("`text` must be a character vector")
  }
  if (!reticulate::py_module_available("portunlp")) {
    stop("Python module 'portunlp' not available. Run `poetry install`.")
  }
  mod <- reticulate::import("portunlp")
  tokens <- lapply(text, mod$spacy_tokenize)
  return(tokens)
}
