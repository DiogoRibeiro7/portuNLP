#pragma once
#include <string>
#include <vector>

/// \brief Split text into lowercase word tokens.
///
/// Tokens consist of letter or digit sequences extracted via a simple
/// UTF-8–aware scan. Punctuation is skipped and ASCII letters are
/// lowercased to keep the tokenizer simple while a FreeLing-based
/// solution is developed.
///
/// \param text Input text.
/// \return Vector of lowercase tokens.
std::vector<std::string> split_words(const std::string& text);
