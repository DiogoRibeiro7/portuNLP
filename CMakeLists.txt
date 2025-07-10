cmake_minimum_required(VERSION 3.15)
project(portuNLP LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_library(portunlp STATIC src/cpp/tokenizer.cpp)
target_include_directories(portunlp PUBLIC include)

add_executable(test_tokenizer tests/cpp/test_tokenizer.cpp)
target_link_libraries(test_tokenizer PRIVATE portunlp)

enable_testing()
add_test(NAME tokenizer COMMAND test_tokenizer)
