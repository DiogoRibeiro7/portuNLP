# AGENTS.md

This document guides how LLM-based agents and contributors interact with the portuNLP project, defining style guidelines, development standards, workflows, and owner information across Python, R, and C++ modules.

## 1. Purpose

Provide clear instructions so that both human developers and an LLM (e.g., GPT) can follow style guidelines, development standards, and workflows when contributing to the repository.

## 2. Documentation and Style

### 2.1 Python

* Every function must include a Google-style docstring.
* Provide concise inline comments when logic is non-obvious.
* Apply full type annotations (`typing` module) and enforce with `mypy`.

### 2.2 R

* Use roxygen2 comments for all exported functions in the R package.
* Keep `README.md` and `NEWS.md` updated with each new feature.

### 2.3 C++

* Target C++17 standard or newer.
* Document all functions and classes with Doxygen-style comments.
* Follow Google C++ style guide for formatting.
* Apply `clang-format` for code formatting; configure settings in `.clang-format`.
* Provide inline comments for complex logic.

## 3. Environment and Setup

### 3.1 Python

1. Use Python 3.10 or newer.
2. Ensure [Poetry](https://python-poetry.org/) is installed.
3. Install Python dependencies:

   ```bash
   poetry install
   ```
4. (Optional) Activate the virtual environment:

   ```bash
   poetry shell
   ```
5. Linting & Formatting: run `pre-commit run --all-files` (Black, isort, flake8).

### 3.2 R

1. Run the setup script to install R, TeX, and dependencies:

   ```bash
   ./setup.sh
   ```
2. Regenerate R package namespace:

   ```r
   devtools::document()
   ```

### 3.3 C++

1. Ensure CMake (version 3.15+) and a C++17 compatible compiler are installed.
2. Build C++ modules:

   ```bash
   mkdir -p build && cd build
   cmake ..
   make
   ```
3. Format C++ code:

   ```bash
   clang-format -i src/cpp/**/*.cpp include/**/*.hpp
   ```

## 4. Project Structure

* **Python**: Managed via Poetry. Update `pyproject.toml` on dependency changes.
* **R**: Metadata in `DESCRIPTION`; regenerate `NAMESPACE` with roxygen2.
* **C++**: Source in `src/cpp/`, headers in `include/`, build managed by CMake in `build/`.

## 5. Testing

* **R**: Run `R CMD check .` at the project root after modifications.
* **Python**: Run `poetry run pytest` for Python tests.
* **C++**: After building, run CTest from the build directory:

  ```bash
  ctest --output-on-failure
  ```

## 6. Instructions for the LLM Agent

### 6.1 Code Conventions

* **Docstrings/Comments**: Google-style for Python, roxygen2 for R, Doxygen for C++.
* **Typing**: Use `typing` in Python; include template or type hints in C++ where possible.
* **Formatting**: `black`/`isort` for Python, `clang-format` for C++, roxygen2 standards in R.
* **Function Length**: Keep functions focused (< 50 lines when possible).
* **Imports/Includes**: Centralize Python imports via isort; C++ includes guarded and ordered.

### 6.2 Development Workflow

1. **Branch Naming**: `feature/<short-description>` or `fix/<short-description>`.
2. **Build & Tests**: Ensure R, Python, and C++ modules build and pass tests (`R CMD check`, `pytest`, `ctest`).
3. **Pre-Commit**: Run `pre-commit run --all-files` and `clang-format` before commit.
4. **Base Branch**: Open PRs against the `main` branch.

## 7. Pull Requests (PRs)

### 7.1 PR Structure

* **Title**: Imperative verb, e.g., `Add data validation`.
* **Description**:

  1. **Context**: Describe the problem or feature.
  2. **Solution**: Summarize changes.
  3. **Build & Tests**: Explain steps to build and tests performed.
  4. **Checklist**:

     * [ ] Code formatted (Black, isort, clang-format)
     * [ ] Type annotations complete (Python) and equivalent in C++
     * [ ] Test coverage adequate for Python/R/C++
     * [ ] `mypy`, `R CMD check`, and `ctest` pass

### 7.2 Best Practices

* **Be Descriptive**: Explain *why* changes were made.
* **Issue References**: Link to issues (e.g., `Closes #123`).
* **Small PRs**: Focus on a single goal.
* **Examples**: Include usage snippets when relevant.

## 8. Owner Information

* **Name**: Diogo Ribeiro
* **Username**: DiogoRibeiro7
* **Personal Email**: [diogo.debastos.ribeiro@gmail.com](mailto:diogo.debastos.ribeiro@gmail.com)
* **Professional Email**: [dfr@esmad.ipp.pt](mailto:dfr@esmad.ipp.pt)
* **Affiliation**: ESMAD - Instituto Politécnico do Porto
* **ORCID**: [https://orcid.org/0009-0001-2022-7072](https://orcid.org/0009-0001-2022-7072)

## 9. Roadmap Awareness

Follow the development stages in `ROADMAP.md`. Ensure new features align with previous steps.

## 10. Examples

### 10.1 Python Docstring

```python
from typing import List

def sum_values(values: List[int]) -> int:
    """
    Sum a list of integers.

    Args:
        values (List[int]): A list of integer values.

    Returns:
        int: The sum of the values.
    """
    return sum(values)
```

### 10.2 C++ Doxygen Example

```cpp
#include <vector>

/// \brief Sum a list of integers.
///
/// \param values A vector of integer values.
/// \return The sum of the values.
int sumValues(const std::vector<int>& values) {
    int total = 0;
    for (int v : values) {
        total += v;
    }
    return total;
}
```

### 10.3 PR Description Example

```
Title: Add email validation to User model

Description:
- **Context**: Ensure valid emails only.
- **Solution**: Implement `validate_email` with regex in Python and exposed to R.
- **Build & Tests**:
  - Python: `pytest` passes.
  - R: `R CMD check` passes.
  - C++: `ctest` passes.

Checklist:
- [x] Code formatted
- [x] Type annotations complete
- [x] Doxygen comments added
- [x] Test coverage > 90%
- [x] mypy, R CMD check, ctest pass

Closes #45
```
