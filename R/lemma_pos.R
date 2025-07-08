#' Lemmatize Portuguese tokens
#'
#' Lemmatize tokens using spaCy if available.
#'
#' Falls back to returning the input tokens when the Python helper cannot be
#' loaded. This keeps the function functional even without Python
#' dependencies.
#'
#' @param tokens Character vector of tokens.
#'
#' @return Character vector of lemmas.
#' @examples
#' lemmatize_pt(c("cachorros", "bonitos"))
#'
#' @export
lemmatize_pt <- function(tokens) {
  if (!is.character(tokens)) {
    stop("`tokens` must be a character vector")
  }

  if (reticulate::py_module_available("portunlp")) {
    mod <- reticulate::import("portunlp")
    lemmas <- mod$spacy_lemmatize(paste(tokens, collapse = " "))
    return(lemmas)
  }

  return(tokens)
}

#' Part-of-speech tagging for Portuguese tokens
#'
#' Generate part-of-speech tags using spaCy when available.
#'
#' Returns "UNK" tags when the Python helper is not installed so that the
#' function degrades gracefully.
#'
#' @param tokens Character vector of tokens.
#'
#' @return Character vector of POS tags corresponding to input tokens.
#' @examples
#' pos_tag_pt(c("O", "gato", "dorme"))
#'
#' @export
pos_tag_pt <- function(tokens) {
  if (!is.character(tokens)) {
    stop("`tokens` must be a character vector")
  }

  if (reticulate::py_module_available("portunlp")) {
    mod <- reticulate::import("portunlp")
    tags <- mod$spacy_pos_tag(paste(tokens, collapse = " "))
    return(tags)
  }

  tags <- rep("UNK", length(tokens))
  return(tags)
}

#' Mapping of spaCy POS tags to Universal POS tags
#'
#' A minimal table that maps spaCy's part-of-speech tags to the
#' corresponding Universal POS tag. This can be used to standardize
#' tagging results across different NLP tools.
#'
#' @format A data frame with columns:
#' \describe{
#'   \item{spacy}{spaCy POS tag}
#'   \item{universal}{Universal POS tag}
#' }
#' @source Manually curated for examples.
#' @examples
#' data(pos_map)
"pos_map"
