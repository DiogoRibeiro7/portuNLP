#include "tokenizer.hpp"

#include <sstream>

std::vector<std::string> split_words(const std::string& text) {
  std::vector<std::string> tokens;
  std::istringstream iss(text);
  for (std::string token; iss >> token;) {
    tokens.push_back(token);
  }
  return tokens;
}
