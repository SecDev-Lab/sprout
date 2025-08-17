# Code Style and Conventions

## Python Style
- Python 3.11+ with type hints
- Use ruff for linting and formatting
- Follow PEP 8 conventions
- Use type annotations for function parameters and return types

## Naming Conventions
- Functions: snake_case (e.g., `parse_env_template`)
- Classes: PascalCase (e.g., `SproutError`)
- Constants: UPPER_CASE
- Type aliases: PascalCase (e.g., `BranchName`, `PortNumber`)

## Documentation
- Use docstrings for functions with Args/Returns sections
- Comments should be in English
- No emoji in code (only in CLI output if requested)

## Error Handling
- Use custom `SproutError` exception for application errors
- Use `typer.Exit()` for CLI exit codes
- Provide helpful error messages to users

## Testing
- Use pytest for testing
- Mock external dependencies (subprocess, file system)
- Use `@pytest.mark.parametrize` for multiple test scenarios
- Test files go in `tests/` directory

## CLI Design
- Use typer for CLI framework
- Use rich for beautiful console output
- Support both interactive and silent modes
- Exit codes: 0 (success), 1 (error), 130 (user cancellation)