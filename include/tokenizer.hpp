#pragma once
#include <string>
#include <vector>

/// \brief Split text into whitespace-delimited tokens.
///
/// \param text Input text.
/// \return Vector of token strings.
std::vector<std::string> split_words(const std::string& text);
