#' Tokenize text using the C++ implementation
#'
#' Calls `cpp_split_words()` to tokenize a character vector using a
#' regular-expression based tokenizer that lowercases tokens. This
#' provides a simple high-performance approach and serves as a placeholder
#' for deeper FreeLing integration.
#'
#' @param text Character vector with input strings.
#'
#' @return A list of character vectors with tokens.
#' @examples
#' tokenize_cpp("O gato dorme")
#' @export
tokenize_cpp <- function(text) {
  if (!is.character(text)) {
    stop("`text` must be a character vector")
  }
  lapply(
    text,
    function(x) .Call("_portuNLP_cpp_split_words", x, PACKAGE = "portuNLP")
  )
}
