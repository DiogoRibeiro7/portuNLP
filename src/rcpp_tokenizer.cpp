#include <Rcpp.h>

#include "tokenizer.hpp"

/// \brief Expose the C++ tokenizer to R.
// [[Rcpp::export]]
Rcpp::CharacterVector cpp_split_words(const std::string& text) {
  return Rcpp::wrap(split_words(text));
}
