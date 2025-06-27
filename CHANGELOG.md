# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- `--path` flag for `sprout create` command to output only the worktree path, enabling one-liner usage like `cd $(sprout create feature --path)`

### Changed

### Deprecated

### Removed

### Fixed

### Security

## [1.0.0] - 2025-06-27

### Added
- Initial implementation of sprout CLI tool
- `create` command to create new git worktrees with Docker Compose support
- `ls` command to list all sprout worktrees
- `rm` command to remove sprout worktrees
- `path` command to get the path of a sprout worktree
- Rich terminal output with progress indicators
- Comprehensive test suite with pytest
- Type checking with mypy
- Linting and formatting with ruff
- CI/CD pipeline with GitHub Actions
- Support for Python 3.11, 3.12, and 3.13

### Changed

### Deprecated

### Removed

### Fixed

### Security

[Unreleased]: https://github.com/SecDev-Lab/sprout/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/SecDev-Lab/sprout/compare/v1.0.0...HEAD
