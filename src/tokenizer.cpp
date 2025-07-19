#include "tokenizer.hpp"

#include <algorithm>
#include <regex>

/**
 * \brief Tokenize a string into words.
 *
 * Tokens are extracted using a Unicode-aware regular expression that matches
 * sequences of letters or digits. Punctuation is discarded and tokens are
 * lowercased to simplify downstream processing. This function is intentionally
 * lightweight but demonstrates how C++ can handle basic normalization without
 * relying on R.
 *
 * \param text Input string to tokenize.
 * \return Vector of tokens in lowercase.
 */
std::vector<std::string> split_words(const std::string& text) {
  static const std::regex word_re("[A-Za-z\xC0-\xFF0-9]+",
                                  std::regex::optimize);
  std::vector<std::string> tokens;
  auto begin = std::sregex_iterator(text.begin(), text.end(), word_re);
  auto end = std::sregex_iterator();
  for (auto it = begin; it != end; ++it) {
    std::string tok = it->str();
    std::transform(tok.begin(), tok.end(), tok.begin(), [](unsigned char c) {
      return static_cast<char>(std::tolower(c));
    });
    tokens.push_back(tok);
  }
  return tokens;
}
