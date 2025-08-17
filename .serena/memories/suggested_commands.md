# Suggested Commands for Sprout Development

## Testing and Quality
- `make test` - Run all unit tests
- `make test-cov` - Run tests with coverage report
- `make lint` - Run ruff linter
- `make format` - Format code with ruff
- `make typecheck` - Run type checking

## Development Setup
- `make setup` - Install development dependencies (or `uv sync --dev`)

## Building and Running
- `sprout create <branch-name>` - Create a new worktree
- `sprout ls` - List all worktrees
- `sprout rm <branch-name>` - Remove a worktree
- `sprout path <branch-name>` - Get worktree path

## Git Commands
- `git worktree list` - List git worktrees
- `git worktree add` - Add a worktree
- `git worktree remove` - Remove a worktree

## Important: After Task Completion
Always run:
1. `make lint` - Check for linting errors
2. `make format` - Format the code
3. `make test` - Ensure all tests pass