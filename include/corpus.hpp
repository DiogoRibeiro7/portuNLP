#pragma once

#include <cstddef>
#include <string>
#include <unordered_map>
#include <vector>

/// \brief Count token frequencies.
///
/// \param tokens Token sequence.
/// \return Mapping of token strings to occurrence counts.
std::unordered_map<std::string, std::size_t> count_term_frequencies(
    const std::vector<std::string>& tokens);

/// \brief Build contiguous n-grams from a token sequence.
///
/// \param tokens Token sequence.
/// \param n N-gram size.
/// \return Vector of contiguous n-grams.
std::vector<std::vector<std::string>> build_ngrams(
    const std::vector<std::string>& tokens, std::size_t n);
