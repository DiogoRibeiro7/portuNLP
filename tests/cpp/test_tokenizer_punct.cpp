#include <cassert>
#include "tokenizer.hpp"

int main() {
  auto tokens = split_words("ola, mundo! tudo bem?");
  assert(tokens.size() == 4);
  assert(tokens[0] == "ola,");
  assert(tokens[1] == "mundo!");
  assert(tokens[2] == "tudo");
  assert(tokens[3] == "bem?");
  return 0;
}
