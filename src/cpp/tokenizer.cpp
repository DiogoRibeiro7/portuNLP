#include "tokenizer.hpp"

#include <cctype>
#include <string>
#include <vector>

std::vector<std::string> split_words(const std::string& text) {
  std::vector<std::string> tokens;
  std::string tok;
  const size_t n = text.size();
  for (size_t i = 0; i < n;) {
    unsigned char c = static_cast<unsigned char>(text[i]);
    if (std::isalnum(c)) {
      tok.push_back(static_cast<char>(std::tolower(c)));
      ++i;
    } else if (c >= 0xC0) {
      size_t len = 1;
      if ((c & 0xE0) == 0xC0) {
        len = 2;
      } else if ((c & 0xF0) == 0xE0) {
        len = 3;
      } else if ((c & 0xF8) == 0xF0) {
        len = 4;
      }
      tok.append(text, i, len);
      i += len;
    } else {
      if (!tok.empty()) {
        tokens.push_back(tok);
        tok.clear();
      }
      ++i;
    }
  }
  if (!tok.empty()) {
    tokens.push_back(tok);
  }
  return tokens;
}
