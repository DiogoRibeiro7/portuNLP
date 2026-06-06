#include <cstddef>
#include <string>
#include <unordered_map>
#include <vector>

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include "corpus.hpp"
#include "tokenizer.hpp"

namespace py = pybind11;

PYBIND11_MODULE(_portunlp_cpp, module) {
  module.doc() = "C++ acceleration for portuNLP";

  module.def("split_words", &split_words, py::arg("text"),
             "Split text into lowercase word tokens.");
  module.def("count_term_frequencies", &count_term_frequencies,
             py::arg("tokens"), "Count token frequencies.");
  module.def("build_ngrams", &build_ngrams, py::arg("tokens"), py::arg("n"),
             "Build contiguous n-grams.");
}
