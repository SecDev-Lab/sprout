# sprout CLI Tool Overview

## Purpose

`sprout` is a CLI tool that automates and simplifies the setup of independent development environments for each branch in development workflows using `git worktree` and `docker compose`.

## Main Features

### 1. Automated Development Environment Setup
- Create git worktrees
- Automatically generate `.env` files from `.env.example` templates
- Automatic port number assignment (collision avoidance)
- Interactive environment variable configuration

### 2. Unified Management
- Centralize all worktrees in `.sprout/` directory
- Management features like list display, deletion, and path retrieval
- Visual display of current worktree

## Design Philosophy

### Pursuit of Simplicity
- Focus on minimum necessary features
- Intuitive command structure
- No configuration files required

### Ensuring Safety
- Confirmation prompts for delete operations
- Proper rollback on errors
- Automatic port collision avoidance

### Improving Development Efficiency
- Environment setup with single command
- Reuse of environment variables (automatic retrieval from shell environment variables)
- Maintain compatibility with Docker Compose variable syntax

## Architecture

### Directory Structure
```
/your-project
├── .git/
├── .sprout/              # sprout management directory
│   └── <branch-name>/    # each worktree
│       ├── .env          # auto-generated environment config
│       └── ...           # source code
├── .env.example          # template
└── compose.yaml          # Docker Compose config
```

### Template Syntax
- `{{ VARIABLE }}`: User input or environment variable
- `{{ auto_port() }}`: Automatic port assignment
- `${...}`: Docker Compose variables (preserved as-is)

## Implementation Details

### Technologies Used
- **Language**: Python 3.11+
- **CLI Framework**: Typer
- **UI**: Rich (colorful output)
- **Package Management**: Hatch, uv

### Error Handling
- Git repository check
- File existence verification
- Port availability validation
- User cancellation support

### Test Strategy
- Unit tests (pytest)
- Integration tests
- External command testing with mocks
- Coverage target: 80% or higher