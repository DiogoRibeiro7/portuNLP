#pragma once
#include <string>
#include <vector>

/// \brief Split UTF-8 text into lowercase word tokens.
///
/// Tokens are maximal runs of word characters: ASCII letters and digits plus
/// the Latin-1 Supplement letters (covering Portuguese accented characters
/// such as á, ã, ç, é, õ, ú). Word characters are lowercased; everything else
/// is treated as a separator. The classification and lowercasing mirror
/// Python's ``str.isalnum()`` / ``str.lower()`` over this character set so the
/// native tokenizer and the pure-Python fallback produce identical output.
///
/// \param text Input UTF-8 text.
/// \return Vector of lowercase UTF-8 tokens.
std::vector<std::string> split_words(const std::string& text);
