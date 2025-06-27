# UAT (User Acceptance Test) Shortcut

## Overview
Command to automate comprehensive verification of Python projects.
Performs code quality checks, tests, and application functionality verification.

## Execution Content

### 1. Code Quality Check
```bash
make format
make lint
```

### 2. Unit Test Execution
```bash
make test
```

### 3. Application Functionality Verification
If the project has a main application (CLI tool, web server, etc.):
- Help message display verification
- Basic startup verification
- Health check (if applicable)

## Pass Criteria
- All commands execute without errors
- Zero lint errors
- All unit tests pass
- Application starts normally (if applicable)

## Example Usage
```bash
# Execute in Claude Code
+uat
```

## Notes
- No impact on actual deployment or production environment
- Tests run in development environment
- Project-specific verification items can be added as needed