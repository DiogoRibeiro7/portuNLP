library(microbenchmark)

#' Benchmark tokenization performance
#'
#' This script measures the throughput of `tokenize_pt()` for a large
#' Portuguese corpus. It outputs the results in milliseconds per call.
#'
#' To run:
#' ```R
#' source("benchmarks/benchmark_tokenize.R")
#' ```
#'
#' @examples
#' # Run from the project root
#' source("benchmarks/benchmark_tokenize.R")
corpus <- rep("O elétrico está em ação.", 1000)
res <- microbenchmark(tokenize_pt(corpus), times = 50)
print(res)

