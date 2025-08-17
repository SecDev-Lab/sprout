# Sprout Project Overview

Sprout is a CLI tool to automate git worktree and Docker Compose development workflows.

## Purpose
- Create isolated development environments using git worktrees
- Automatic `.env` file generation from `.env.example` templates
- Smart port allocation to avoid conflicts
- Centralized worktree management in `.sprout/` directory

## Tech Stack
- Language: Python 3.11+
- Build System: Makefile with uv package manager
- Testing: pytest
- Code Quality: ruff (linting and formatting)
- CLI Framework: typer
- UI: rich (for beautiful CLI output)

## Key Features
1. Creates git worktrees with automatic branch creation
2. Processes `.env.example` templates to generate `.env` files
3. Supports variable placeholders: `{{ VARIABLE_NAME }}`
4. Supports automatic port assignment: `{{ auto_port() }}`
5. Works with monorepos (multiple `.env.example` files in subdirectories)
6. Works without `.env.example` files (just creates worktrees)

## Entry Points
- Main CLI: `src/sprout/cli.py`
- Commands: `src/sprout/commands/` (create, ls, rm, path)
- Template parsing: `src/sprout/utils.py::parse_env_template()`