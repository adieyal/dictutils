# AGENTS.md

## Build, Lint, and Test Commands
- Install dependencies: `pip install -r requirements-dev.txt`
- Install package with dev extras: `pip install .[test,typecheck]`
- Run all tests: `pytest`
- Run a single test: `pytest -k <testname>`
- Type checking: `mypy dictutils`
- Linting: `ruff dictutils`
- Formatting: `black dictutils`
- Pre-commit hooks: `pre-commit install` (then hooks run on commit)

## Code Style Guidelines
- Follow PEP 8 for formatting and naming conventions.
- Use absolute imports (e.g., `from dictutils.qsdict import qsdict`).
- Type hints are required for all public functions (use modern Python 3.9+ syntax).
- Use docstrings for all public functions and modules.
- Variable, function, and file names should be lowercase_with_underscores.
- Class names should use CamelCase.
- Prefer exceptions for error handling; raise specific errors (e.g., `TypeError`, `ValueError`).
- Keep functions small and focused; avoid deep nesting.
- Use pytest for all tests; place them in the `tests/` directory.
- Test function names should start with `test_` followed by module name (e.g., `test_qsdict_basic_input`).
- Do not include print statements or logging in library code.
- Support Python 3.9+ only.

## Module-Specific Guidelines
- **mergedict**: Always pass `update` parameter to recursive calls; accept `Mapping` but return `dict`.
- **qsdict**: Support both strict and non-strict modes; use plain `dict` (not OrderedDict) everywhere.
- **pivot**: Validate `order` indices in `rearrange` function; add proper error handling.
- **nestagg**: Support `finalize` hooks in `Agg` for post-processing; document dotted path support.

_No Cursor or Copilot rules detected._