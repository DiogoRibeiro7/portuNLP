#include <cassert>

#include "tokenizer.hpp"

int main() {
  auto tokens = split_words("");
  assert(tokens.empty());
  return 0;
}
