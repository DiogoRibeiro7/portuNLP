#include <cassert>

#include "tokenizer.hpp"

int main() {
  auto tokens = split_words("O gato dorme");
  assert(tokens.size() == 3);
  assert(tokens[0] == "o");
  assert(tokens[1] == "gato");
  assert(tokens[2] == "dorme");
  return 0;
}
