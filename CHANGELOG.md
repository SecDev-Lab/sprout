# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Support for multiple `.env.example` files throughout the repository, enabling monorepo workflows
- Recursive scanning of `.env` files for port allocation to ensure global uniqueness across all services

### Changed
- Port allocation now ensures uniqueness across all services in all worktrees, preventing Docker host port conflicts
- `sprout create` now processes all `.env.example` files found in the repository while maintaining directory structure

### Deprecated

### Removed

### Fixed

### Security

## [0.3.0] - 2025-06-27

### Added
- `--path` flag for `sprout create` command to output only the worktree path, enabling one-liner usage like `cd $(sprout create feature --path)`

### Changed
- Enhanced `sprout path` and `sprout rm` commands to accept index numbers from `sprout ls` output, enabling faster navigation without typing full branch names (e.g., `cd $(sprout path 2)` instead of `cd $(sprout path feature-long-branch-name)`)

### Deprecated

### Removed

### Fixed

### Security

## [0.2.0] - 2025-06-27

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

[Unreleased]: https://github.com/SecDev-Lab/sprout/compare/v0.3.0...HEAD
[0.2.0]: https://github.com/SecDev-Lab/sprout/compare/v0.2.0...HEAD

[0.3.0]: https://github.com/SecDev-Lab/sprout/compare/v0.3.0...HEAD
