#include "corpus.hpp"

#include <cstddef>
#include <string>
#include <unordered_map>
#include <vector>

std::unordered_map<std::string, std::size_t> count_term_frequencies(
    const std::vector<std::string>& tokens) {
  std::unordered_map<std::string, std::size_t> frequencies;
  for (const auto& token : tokens) {
    ++frequencies[token];
  }
  return frequencies;
}

std::vector<std::vector<std::string>> build_ngrams(
    const std::vector<std::string>& tokens, std::size_t n) {
  std::vector<std::vector<std::string>> ngrams;
  if (n == 0 || n > tokens.size()) {
    return ngrams;
  }

  ngrams.reserve(tokens.size() - n + 1);
  for (std::size_t index = 0; index + n <= tokens.size(); ++index) {
    ngrams.emplace_back(tokens.begin() + static_cast<std::ptrdiff_t>(index),
                        tokens.begin() +
                            static_cast<std::ptrdiff_t>(index + n));
  }
  return ngrams;
}
