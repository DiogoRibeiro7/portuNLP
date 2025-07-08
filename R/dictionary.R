#' Load a custom dictionary
#'
#' Reads a text file containing one word per line and returns a
#' character vector. This is a simple loader for Portuguese
#' dictionaries or wordlists.
#'
#' @param path Path to a text file.
#'
#' @return Character vector of dictionary terms.
#' @examples
#' dict_path <- system.file("extdata", "sample_dict.txt", package = "portuNLP")
#' load_dict(dict_path)
#' @export
load_dict <- function(path) {
  if (!file.exists(path)) {
    stop("File not found: ", path)
  }
  lines <- readLines(path, encoding = "UTF-8", warn = FALSE)
  lines <- trimws(lines)
  lines <- lines[nzchar(lines)]
  return(lines)
}

#' Apply orthographic rules to text
#'
#' Replaces variant-specific spellings using the built-in `orth_rules`
#' data set. Each rule should be formatted as "from -> to".
#'
#' @param text Character vector with input text.
#' @param rules Data frame of orthographic rules. Defaults to
#'   `orth_rules`.
#'
#' @return Character vector with replacements applied.
#' @examples
#' apply_orth_rules("acto", orth_rules)
#' @export
apply_orth_rules <- function(text, rules = orth_rules) {
  if (!is.character(text)) {
    stop("`text` must be a character vector")
  }
  result <- text
  for (r in rules$rule) {
    parts <- strsplit(r, " -> ")[[1]]
    if (length(parts) == 2) {
      result <- gsub(parts[1], parts[2], result, fixed = TRUE)
    }
  }
  result
}

#' Sample orthographic rules for Portuguese variants
#'
#' A minimal data frame illustrating orthographic differences
#' between European (EU) and Brazilian (BR) Portuguese.
#'
#' @format A data frame with columns:
#' \describe{
#'   \item{variant}{"EU" or "BR"}
#'   \item{rule}{Rule description}
#' }
#' @source Manually curated for examples.
#' @examples
#' data(orth_rules)
"orth_rules"
