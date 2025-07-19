#include "tokenizer.hpp"

#include <sstream>

/**
 * \brief Tokenize a string into words.
 *
 * This simple tokenizer also strips basic punctuation prior to splitting on
 * whitespace. It serves as a lightweight alternative to the R implementation
 * and a stepping stone toward a more advanced FreeLing-based tokenizer.
 *
 * \param text Input string to tokenize.
 * \return Vector of tokens.
 */
std::vector<std::string> split_words(const std::string& text) {
  std::string cleaned;
  cleaned.reserve(text.size());
  for (char ch : text) {
    if (std::ispunct(static_cast<unsigned char>(ch))) {
      cleaned.push_back(' ');
    } else {
      cleaned.push_back(ch);
    }
  }

  std::vector<std::string> tokens;
  std::istringstream iss(cleaned);
  for (std::string token; iss >> token;) {
    tokens.push_back(token);
  }
  return tokens;
}
