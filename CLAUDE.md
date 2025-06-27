# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Work Attitude and Quality Management

**IMPORTANT**: Claude Code should act as a careful veteran engineer. Prioritize quality and reliability over implementation speed.

### Basic Attitude
- Critically verify when you think implementation is complete
- Not just "it works" but always ask "does it really work correctly?"
- Actively consider potential problems and edge cases
- Don't be lazy about testing and verification, be more thorough than necessary
- Always be skeptical of your own implementation and verify from multiple perspectives

### Pre-Implementation Checklist
- Detailed investigation of existing code (related files, dependencies, impact scope)
- Understanding design patterns and coding conventions
- Consider test case coverage
- Verify error handling adequacy

### Post-Implementation Required Verification
1. **Code Quality**: Static analysis with `make lint`, `make format`
2. **Unit Tests**: Run all package tests with `make test`
3. **Integration Tests**: Comprehensive functionality verification
4. **Manual Verification**: Confirm operation with actual use cases
5. **Error Cases**: Verify behavior in abnormal conditions
6. **Performance**: Test under unexpected load
7. **Compatibility**: Confirm no impact on existing features

### Quality Standards
- All tests passing is minimum requirement
- Zero static analysis errors is a prerequisite
- Confirmed to work in actual usage scenarios
- Appropriate behavior for edge cases and error conditions
- Documentation updated (as needed)

## Language Settings

Responses and documentation should be written in English. Always use English for:
- Comments, variable names, and function names in code
- All documentation files
- All communication

## Specification Management

When developing new features, place specifications under `docs/(feature-name)/*.md`.
These specifications serve as references during implementation, but their main purpose is to look back on "what was the purpose, how, and what was implemented" after implementation.

## Intermediate File Management

### Using tmp/ Directory
All intermediate files created by Claude Code (test files, planning documents, temporary work files, etc.) must be created under the `tmp/` directory.

**Target Files**:
- Sample files for testing
- Implementation planning documents
- Temporary debugging files
- Verification scripts
- Other temporary work files

**Exceptions**:
- Official project files (source code, configuration files, official documentation, etc.)
- When user explicitly specifies a different location

### Cleanup
The `tmp/` directory is cleaned up periodically:
- During branch review
- During quality management task execution

## Python Development Workflow

### Setup
```bash
# Install dependencies
make setup  # or uv sync --dev
```

### Testing and Quality Management
```bash
# Code quality check
make lint    # lint with ruff
make format  # format with ruff

# Run tests
make test         # run all tests
make test-cov     # run tests with coverage
```

### Development Considerations
- Mock external dependencies in unit tests
- Use `.env` files for environment configuration
- Use `@pytest.mark.parametrize` for multiple test scenarios
- Utilize `asyncio` for asynchronous processing

## Shortcut Commands

This project supports shortcut commands defined in the `.claude/shortcuts/` directory.

### Usage Rules
- When receiving commands in `+***` format, refer to `.claude/shortcuts/***.md` file
- Display error message if the corresponding shortcut file doesn't exist
- Execute processing according to the contents of the shortcut file

### Available Shortcuts
- `+tn`: Terminal notification (sound notification)
- `+brc`: Branch review & cleanup
- `+uat`: User Acceptance Testing (comprehensive execution of code quality check, unit tests, and application functionality verification)
- `+review`: GitHub PR review

## Task Completion Notification

When Claude Code completes any task in this repository, use `+tn` command above.

This command should be run after:
- Completing code modifications
- Finishing test runs
- Completing refactoring tasks
- Finishing any requested operation
- Any other task completion