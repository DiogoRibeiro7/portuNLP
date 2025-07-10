#' Map spaCy POS tags to Universal POS tags
#'
#' Converts part-of-speech tags produced by spaCy to the Universal
#' POS tagset using the built-in `pos_map` data frame. Tags that are
#' not found in the mapping are returned unchanged.
#'
#' @param tags Character vector of spaCy part-of-speech tags.
#'
#' @return Character vector of Universal POS tags.
#' @examples
#' map_pos_tags(c("NOUN", "VERB"))
#' @export
map_pos_tags <- function(tags) {
  if (!is.character(tags)) {
    stop("`tags` must be a character vector")
  }
  idx <- match(tags, pos_map$spacy)
  mapped <- pos_map$universal[idx]
  mapped[is.na(mapped)] <- tags[is.na(mapped)]
  return(mapped)
}
