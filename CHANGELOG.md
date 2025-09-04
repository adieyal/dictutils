# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.1] - 2025-09-04

### Added
- **Enhanced README.md**: Comprehensive examples with real-world use cases
  - Added Quick Examples section showcasing all major features
  - Added Real-World Examples (sales analysis, configuration management) 
  - Expanded dictutils.ops module documentation with detailed code samples
  - Added status badges for documentation and CI
  - Complete documentation links to Read the Docs pages
- **Documentation improvements**: Complete GitHub repository integration
  - Added GitHub links throughout all documentation pages
  - Configured Sphinx with GitHub source navigation
  - Added contribution callouts and issue reporting guidance
  - Enhanced navigation with external links (GitHub, PyPI, Issues)
- **Comprehensive CHANGELOG.md**: Complete project history documentation
  - Detailed migration guide from 0.1.x to 1.0.0
  - Full historical release notes with context
  - Security updates timeline and dependency management

### Changed
- **Documentation theme**: Switched from Furo to Alabaster
  - Clean, minimal design optimized for technical documentation
  - Improved GitHub integration with star button and banner
  - Custom navigation links to PyPI, Issues, and Changelog
  - Responsive layout with fixed sidebar navigation
- **Project metadata**: Enhanced pyproject.toml with complete URL links
  - Added Documentation, Issues, and Changelog URLs
  - Improved discoverability and project navigation

### Technical
- **Documentation build system**: Improved reliability and performance
  - Fixed Sphinx configuration for better GitHub integration
  - Optimized theme configuration for faster loading
  - Enhanced development workflow with better error handling

---

## [1.0.0] - 2025-09-04

### Major Release - Breaking Changes

This is a complete modernization of the dictutils package, with significant breaking changes and new functionality.

#### Added
- **New `nestagg` module**: Flexible nested aggregation with declarative `Agg` specifications
  - Support for custom `map`, `reduce`, `zero`, `skip_none`, and `finalize` functions
  - Dotted path support for deep attribute access
  - Configurable row inclusion for debugging/inspection
- **New `ops` module**: 20+ utilities for advanced dict manipulation
  - Path-based operations: `deep_get`, `deep_set`, `deep_del`, `deep_has`, `deep_update`
  - Functional operations: `map_keys`, `map_values`, `map_items`, `project`, `where`
  - Aggregation functions: `group_by`, `count_by`, `sum_by`, `reduce_by`, `distinct_by`
  - Schema operations: `schema_check`, `coalesce_paths`, `ensure_path`
  - Tree operations: `flatten_paths`, `expand_paths`, `rollup_tree`
  - List operations: `merge_lists_by`, `index_by`
  - Utility functions: `match`, `patch`, `prune`, `rename_keys`, `transpose_dict`
- **Modern packaging**: Complete migration to PEP 621 `pyproject.toml`
  - Optional dependencies: `[test]`, `[typecheck]`, `[lint]`, `[docs]`
  - Proper entry points and metadata
- **Comprehensive CI/CD pipeline**:
  - GitHub Actions workflow for testing, linting, and type checking
  - Documentation building and deployment workflow
  - Pre-commit hooks configuration
  - Read the Docs integration
- **Complete documentation system**:
  - Sphinx + MyST parser setup
  - API reference with auto-generated docs
  - Cookbooks and quickstart guides  
  - Multiple output formats support
- **Type system enhancements**:
  - Full Python 3.9+ type annotations throughout
  - `py.typed` marker for type checker support
  - Modern union syntax compatibility
- **Enhanced testing infrastructure**:
  - Expanded test coverage with 60+ test cases
  - Property-based testing for edge cases
  - Integration tests for complex workflows

#### Changed
- **BREAKING**: Minimum Python version raised to 3.9+ (dropped 3.4-3.8 support)
- **qsdict**: Added `strict` mode for KeyError on missing keys/attributes
- **mergedict**: Fixed critical recursive `update` parameter bug
- **pivot**: Enhanced with proper error handling and validation
- **mergedict**: Improved type safety and Mapping compatibility
- **qsdict**: Replaced OrderedDict with plain dict (Python 3.7+ dict ordering)
- **All modules**: Comprehensive docstring and type annotation updates
- **Import surface**: Clean top-level imports: `from dictutils import qsdict, mergedict, pivot, Agg, nest_agg`

#### Fixed
- **mergedict**: Recursive calls now properly pass `update` parameter (critical bug fix)
- **qsdict**: Proper handling of missing keys in non-strict mode
- **pivot**: Added validation for `order` parameter indices
- **mergedict**: Fixed handling of None values and edge cases
- **Type compatibility**: Resolved Union syntax for Python 3.9 compatibility

#### Removed
- **BREAKING**: Legacy setup.py, setup.cfg, MANIFEST files
- **BREAKING**: Python 2.7 and Python 3.4-3.8 support
- **BREAKING**: OrderedDict dependency in qsdict
- Dead code and unused imports throughout codebase

#### Security
- Updated all dependencies to latest secure versions
- Removed potential security vulnerabilities in legacy dependencies

---

## [0.1.6] - 2020-09-19

### Added
- Type annotations for better IDE support and type checking
- MyPy integration in Travis CI

### Fixed
- Bug with subclassed dicts (e.g., OrderedDict) in mergedict
- Dict test compatibility issues
- Type annotation compatibility with different Python versions

### Changed
- Reverted to using `tuple` instead of `Tuple` for broader compatibility
- Improved generic type handling

## [0.1.5] - 2020-09-19

### Changed
- Version bump with minor improvements

## [0.1.2] - 2020-09-19

### Fixed
- Generic type checking for Tuple vs tuple compatibility

## [0.1.1] - 2020-06-13

### Added
- Type annotations throughout the codebase
- MyPy support in Travis CI configuration

### Fixed
- Bug that caused issues with subclassed dicts like OrderedDict

## [0.1.0] - 2020-05-08

### Added
- Initial release of dictutils
- **qsdict**: Convert list of dicts/objects into nested dicts
- **mergedict**: Merge nested dictionaries with conflict resolution
- **pivot**: Pivot nested dictionaries by key order
- Basic testing infrastructure
- Travis CI integration
- Python 3.4+ support (initially included Python 2.7, later removed)

### Features
- Support for callable selectors in qsdict
- Multiple dict merging with `*args` support in mergedict
- Flexible pivot operations with custom key ordering
- Comprehensive README with examples

---

## Dependencies and Security Updates

Between releases, the project received multiple dependency updates via Dependabot:

- **2023-10-18**: urllib3 1.25.9 → 1.26.18 (security)
- **2023-08-19**: requests 2.23.0 → 2.31.0 (security)  
- **2023-08-19**: pygments 2.6.1 → 2.15.0 (security)
- **2023-08-17**: certifi 2020.4.5.1 → 2023.7.22 (security)
- Various other dependency updates for security and compatibility

---

## Migration Guide

### Upgrading from 0.1.x to 1.0.0

#### Breaking Changes
1. **Python Version**: Upgrade to Python 3.9 or later
2. **Imports**: Update imports to use the new clean surface:
   ```python
   # Old (still works)
   from dictutils.qsdict import qsdict
   
   # New (recommended)
   from dictutils import qsdict, mergedict, pivot, Agg, nest_agg
   ```

3. **qsdict strict mode**: The new `strict=True` parameter will raise KeyError for missing keys:
   ```python
   # Old behavior (missing keys return None)
   result = qsdict(data, "missing_key")
   
   # New explicit behavior
   result = qsdict(data, "missing_key", strict=False)  # Same as old
   result = qsdict(data, "missing_key", strict=True)   # Raises KeyError
   ```

#### New Functionality
- Explore the new `ops` module for powerful dict manipulation utilities
- Use `nest_agg` for sophisticated aggregation scenarios
- Leverage the comprehensive type system for better IDE support

#### Recommended Actions
1. Update your Python environment to 3.9+
2. Install with appropriate extras: `pip install dictutils[test,typecheck]`
3. Run your existing tests to ensure compatibility
4. Consider adopting new utilities from `ops` module for better performance
5. Enable type checking with mypy for enhanced development experience

For detailed API documentation, visit: [dictutils documentation](https://dictutils.readthedocs.io/)