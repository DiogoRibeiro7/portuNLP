#include <cassert>
#include <string>

#include "tokenizer.hpp"

// Inputs and expectations use explicit UTF-8 byte escapes so the test does not
// depend on the source-file encoding. Each \x escape is followed by another
// escape or a non-hex character to avoid greedy hex parsing.

int main() {
  // "Olá MundÓ" ("Olá MundÓ") -> ["olá", "mundó"]
  // The upper-case "Ó" (Ó) must be lowercased to "ó" (ó).
  auto mixed = split_words("Ol\xC3\xA1 Mund\xC3\x93");
  assert(mixed.size() == 2);
  assert(mixed[0] == "ol\xC3\xA1");    // "olá"
  assert(mixed[1] == "mund\xC3\xB3");  // "mundó"

  // "ÀÇÃO" ("ÀÇÃO") -> single token "àção"
  auto accents = split_words("\xC3\x80\xC3\x87\xC3\x83O");
  assert(accents.size() == 1);
  assert(accents[0] == "\xC3\xA0\xC3\xA7\xC3\xA3o");  // "àção"

  // The multiplication sign "×" is not a word character: it separates.
  auto times = split_words("a\xC3\x97""b");
  assert(times.size() == 2);
  assert(times[0] == "a");
  assert(times[1] == "b");

  return 0;
}
