#pragma once
#include <string>
#include <vector>

/// \brief Split text into whitespace-delimited tokens.
///
/// Basic punctuation is replaced with spaces prior to splitting. This remains a
/// lightweight fallback while more advanced tokenizers are being integrated.
///
/// \param text Input text.
/// \return Vector of token strings.
std::vector<std::string> split_words(const std::string& text);
