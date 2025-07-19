library(microbenchmark)

#' Benchmark the performance of `tokenize_pt()`
#'
#' This helper repeatedly tokenizes a character vector and returns the
#' microbenchmark summary as well as the calculated tokens-per-second
#' throughput.
#'
#' @param corpus Character vector with Portuguese text to tokenize.
#' @param times Number of repetitions for the benchmark.
#'
#' @return A list with the microbenchmark result and the tokens per second.
#'
#' @examples
#' # From the project root run:
#' # source("benchmarks/benchmark_tokenize.R")
#' # benchmark_tokenize(rep("O elétrico está em ação.", 1000))
benchmark_tokenize <- function(corpus, times = 50) {
  res <- microbenchmark(tokenize_pt(corpus), times = times)
  tokens <- length(unlist(strsplit(paste(corpus, collapse = " "), "\s+")))
  throughput <- tokens / median(res$time / 1e9)
  list(result = res, tokens_per_sec = throughput)
}

if (identical(environment(), globalenv())) {
  corpus <- rep("O elétrico está em ação.", 1000)
  out <- benchmark_tokenize(corpus)
  print(out$result)
  cat(sprintf("Median tokens/sec: %.2f\n", out$tokens_per_sec))
}

