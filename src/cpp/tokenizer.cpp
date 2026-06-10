#include "tokenizer.hpp"

#include <cstddef>
#include <cstdint>
#include <string>
#include <vector>

namespace {

/// \brief Decode one UTF-8 code point starting at index \p i.
///
/// Advances \p i past the consumed bytes. On a malformed or truncated
/// sequence the leading byte is returned verbatim and \p i advances by one,
/// so scanning always makes forward progress.
///
/// \param text Input UTF-8 buffer.
/// \param i In/out cursor; updated to the next unread byte.
/// \return The decoded Unicode code point.
std::uint32_t decode_utf8(const std::string& text, std::size_t& i) {
  const std::size_t n = text.size();
  const unsigned char lead = static_cast<unsigned char>(text[i]);

  if (lead < 0x80) {
    ++i;
    return lead;
  }

  std::uint32_t code_point = 0;
  std::size_t continuation_bytes = 0;
  if ((lead & 0xE0) == 0xC0) {
    code_point = lead & 0x1F;
    continuation_bytes = 1;
  } else if ((lead & 0xF0) == 0xE0) {
    code_point = lead & 0x0F;
    continuation_bytes = 2;
  } else if ((lead & 0xF8) == 0xF0) {
    code_point = lead & 0x07;
    continuation_bytes = 3;
  } else {
    ++i;  // Invalid leading byte.
    return lead;
  }

  std::size_t cursor = i + 1;
  for (std::size_t k = 0; k < continuation_bytes; ++k, ++cursor) {
    if (cursor >= n ||
        (static_cast<unsigned char>(text[cursor]) & 0xC0) != 0x80) {
      ++i;  // Truncated or invalid continuation.
      return lead;
    }
    code_point = (code_point << 6) |
                 (static_cast<unsigned char>(text[cursor]) & 0x3F);
  }

  i = cursor;
  return code_point;
}

/// \brief Append a code point to \p out as UTF-8.
///
/// \param code_point Unicode code point to encode.
/// \param out Destination buffer.
void encode_utf8(std::uint32_t code_point, std::string& out) {
  if (code_point < 0x80) {
    out.push_back(static_cast<char>(code_point));
  } else if (code_point < 0x800) {
    out.push_back(static_cast<char>(0xC0 | (code_point >> 6)));
    out.push_back(static_cast<char>(0x80 | (code_point & 0x3F)));
  } else if (code_point < 0x10000) {
    out.push_back(static_cast<char>(0xE0 | (code_point >> 12)));
    out.push_back(static_cast<char>(0x80 | ((code_point >> 6) & 0x3F)));
    out.push_back(static_cast<char>(0x80 | (code_point & 0x3F)));
  } else {
    out.push_back(static_cast<char>(0xF0 | (code_point >> 18)));
    out.push_back(static_cast<char>(0x80 | ((code_point >> 12) & 0x3F)));
    out.push_back(static_cast<char>(0x80 | ((code_point >> 6) & 0x3F)));
    out.push_back(static_cast<char>(0x80 | (code_point & 0x3F)));
  }
}

/// \brief Whether a code point is a word character.
///
/// Covers ASCII letters and digits plus the Latin-1 Supplement letters
/// (U+00C0–U+00FF, excluding the × and ÷ signs). This mirrors Python's
/// ``str.isalnum()`` exactly over that range so the native tokenizer and the
/// pure-Python fallback produce identical output. Callers route only text
/// within this character set to the native path.
///
/// \param code_point Unicode code point.
/// \return True when the code point belongs to a word.
bool is_word_codepoint(std::uint32_t code_point) {
  if (code_point >= '0' && code_point <= '9') {
    return true;
  }
  if (code_point >= 'A' && code_point <= 'Z') {
    return true;
  }
  if (code_point >= 'a' && code_point <= 'z') {
    return true;
  }
  if (code_point >= 0x00C0 && code_point <= 0x00FF && code_point != 0x00D7 &&
      code_point != 0x00F7) {
    return true;
  }
  return false;
}

/// \brief Lowercase a word code point within the supported character set.
///
/// Handles ASCII ``A``–``Z`` and the upper-case Latin-1 letters
/// (U+00C0–U+00DE, excluding ×). Other code points are returned unchanged,
/// matching ``str.lower()`` over the supported set.
///
/// \param code_point Unicode code point.
/// \return The lower-case code point.
std::uint32_t to_lower_codepoint(std::uint32_t code_point) {
  if (code_point >= 'A' && code_point <= 'Z') {
    return code_point + 0x20;
  }
  if (code_point >= 0x00C0 && code_point <= 0x00DE && code_point != 0x00D7) {
    return code_point + 0x20;
  }
  return code_point;
}

}  // namespace

std::vector<std::string> split_words(const std::string& text) {
  std::vector<std::string> tokens;
  std::string current;
  const std::size_t n = text.size();

  std::size_t i = 0;
  while (i < n) {
    const std::uint32_t code_point = decode_utf8(text, i);
    if (is_word_codepoint(code_point)) {
      encode_utf8(to_lower_codepoint(code_point), current);
    } else if (!current.empty()) {
      tokens.push_back(current);
      current.clear();
    }
  }

  if (!current.empty()) {
    tokens.push_back(current);
  }
  return tokens;
}
