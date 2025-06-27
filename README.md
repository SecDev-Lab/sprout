# sprout

A CLI tool to automate git worktree and Docker Compose development workflows.

## Features

- 🌱 Create isolated development environments using git worktrees
- 🔧 Automatic `.env` file generation from templates
- 🚢 Smart port allocation to avoid conflicts
- 📁 Centralized worktree management in `.sprout/` directory
- 🎨 Beautiful CLI interface with colors and tables

## Installation

```bash
pip install sprout
```

For development:
```bash
# Clone the repository
git clone https://github.com/SecDev-Lab/sprout.git
cd sprout

# Install in development mode
pip install -e ".[dev]"
```

## Quick Start

1. Create a `.env.example` template in your project root:
```env
# API Configuration
API_KEY={{ API_KEY }}
API_PORT={{ auto_port() }}

# Database Configuration  
DB_HOST=localhost
DB_PORT={{ auto_port() }}

# Example: Docker Compose variables (preserved as-is)
# sprout will NOT process ${...} syntax - it's passed through unchanged
# DB_NAME=${DB_NAME}
```

2. Create and navigate to a new development environment in one command:
```bash
cd $(sprout create feature-branch --path)
```

This single command:
- Creates a new git worktree for `feature-branch`
- Generates a `.env` file from your template
- Outputs the path to the new environment
- Changes to that directory when wrapped in `cd $(...)`

3. Start your services:
```bash
docker compose up -d
```

### Alternative: Two-Step Process

If you prefer to see the creation output first:
```bash
# Create the environment
sprout create feature-branch

# Then navigate to it
cd $(sprout path feature-branch)
```

## Commands

### `sprout create <branch-name> [--path]`
Create a new development environment with automated setup.

Options:
- `--path`: Output only the worktree path (useful for shell command substitution)

Examples:
```bash
# Create and see progress messages
sprout create feature-xyz

# Create and navigate in one command
cd $(sprout create feature-xyz --path)
```

### `sprout ls`
List all managed development environments with their status.

### `sprout rm <branch-name>`
Remove a development environment (with confirmation prompts).

### `sprout path <branch-name>`
Get the filesystem path of a development environment.

### `sprout --version`
Show the version of sprout.

## Template Syntax

sprout supports two types of placeholders in `.env.example`:

1. **Variable Placeholders**: `{{ VARIABLE_NAME }}`
   - **First**: Checks if the variable exists in your environment (e.g., `export API_KEY=xxx`)
   - **Then**: If not found in environment, prompts for user input
   - Example: `{{ API_KEY }}` will use `$API_KEY` if set, otherwise asks you to enter it

2. **Auto Port Assignment**: `{{ auto_port() }}`
   - Automatically assigns available ports
   - Avoids conflicts with other sprout environments
   - Checks system port availability

3. **Docker Compose Syntax (Preserved)**: `${VARIABLE}`
   - NOT processed by sprout - passed through as-is
   - Useful for Docker Compose variable substitution
   - Example: `${DB_NAME:-default}` remains unchanged in generated `.env`

### Environment Variable Resolution Example

```bash
# Set environment variable
export API_KEY="my-secret-key"

# Create sprout environment - API_KEY will be automatically used
sprout create feature-branch
# → API_KEY in .env will be set to "my-secret-key" without prompting

# For unset variables, sprout will prompt
sprout create another-branch
# → Enter a value for 'DATABASE_URL': [user input required]
```

## Documentation

- [Architecture Overview](docs/sprout-cli/overview.md) - Design philosophy, architecture, and implementation details
- [Detailed Usage Guide](docs/sprout-cli/usage.md) - Comprehensive usage examples and troubleshooting

## Development

### Setup
```bash
# Install development dependencies
make setup
```

### Testing
```bash
# Run tests
make test

# Run tests with coverage
make test-cov
```

### Code Quality
```bash
# Run linter
make lint

# Format code
make format

# Run type checking
make typecheck
```

## Requirements

- Python 3.11+
- Git
- Docker Compose (optional, for Docker-based workflows)

## License

See LICENSE file.
