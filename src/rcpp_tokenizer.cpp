#include <Rcpp.h>
#include "tokenizer.hpp"

// [[Rcpp::export]]
Rcpp::CharacterVector cpp_split_words(const std::string& text) {
  return Rcpp::wrap(split_words(text));
}
