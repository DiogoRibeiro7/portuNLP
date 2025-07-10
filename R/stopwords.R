#' Get Portuguese stopwords
#'
#' Returns a vector of built-in Portuguese stopwords with optional
#' additions or removals.
#'
#' @param extra Optional character vector of custom stopwords to add.
#' @param omit Optional character vector of stopwords to remove.
#'
#' @return Character vector of stopwords.
#' @examples
#' get_stopwords()
#' get_stopwords(extra = c("novapalavra"))
#' @export
get_stopwords <- function(extra = NULL, omit = NULL) {
  words <- stopwords_pt
  if (!is.null(extra)) {
    words <- unique(c(words, extra))
  }
  if (!is.null(omit)) {
    words <- setdiff(words, omit)
  }
  return(words)
}

#' Portuguese stopword list
#'
#' A small sample of common Portuguese stopwords used by `get_stopwords()`.
#'
#' @format Character vector of stopwords.
#' @source Derived from freely available lists.
#' @examples
#' data(stopwords_pt)
"stopwords_pt"
