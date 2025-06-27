# sprout Usage Guide

## Installation

```bash
# Development installation
pip install -e .

# Or standard installation
pip install .
```

## Basic Usage

### 1. Create New Development Environment

```bash
sprout create feature-branch
```

This command performs:
1. Creates worktree in `.sprout/feature-branch`
2. Generates `.env` from `.env.example` template
3. Prompts for required environment variables
4. Automatically assigns port numbers

### 2. List Development Environments

```bash
sprout ls
```

Example output:
```
                    Sprout Worktrees                    
┏━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┓
┃ Branch        ┃ Path                    ┃ Status   ┃ Last Modified   ┃
┡━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━━━━┩
│ feature-auth  │ .sprout/feature-auth    │ ● current│ 2024-01-15 14:30│
├───────────────┼─────────────────────────┼──────────┼─────────────────┤
│ feature-ui    │ .sprout/feature-ui      │          │ 2024-01-14 10:15│
└───────────────┴─────────────────────────┴──────────┴─────────────────┘
```

### 3. Remove Development Environment

```bash
sprout rm feature-branch
```

Displays confirmation prompts:
- Worktree removal confirmation
- Git branch removal confirmation (optional)

### 4. Get Development Environment Path

```bash
# Display path
sprout path feature-branch

# Navigate directly
cd $(sprout path feature-branch)
```

## Writing .env.example Templates

### Basic Environment Variables
```env
DATABASE_URL={{ DATABASE_URL }}
API_KEY={{ API_KEY }}
```

### Automatic Port Assignment
```env
WEB_PORT={{ auto_port() }}
API_PORT={{ auto_port() }}
DB_PORT={{ auto_port() }}
```

### Docker Compose Variables (Preserved As-Is)
```env
COMPOSE_PROJECT_NAME=${COMPOSE_PROJECT_NAME:-myproject}
```

### Fixed Values
```env
ENVIRONMENT=development
DEBUG=true
```

## Practical Examples

### 1. Running Multiple Development Environments in Parallel

```bash
# Develop authentication feature
sprout create feature-auth
cd .sprout/feature-auth
docker compose up -d

# Develop UI improvements (in another terminal)
sprout create feature-ui  
cd .sprout/feature-ui
docker compose up -d

# Ports are automatically assigned different numbers
```

### 2. Pre-setting Environment Variables

```bash
# Set environment variables in shell
export API_KEY="my-secret-key"
export DATABASE_URL="postgres://localhost/mydb"

# sprout automatically uses these values
sprout create feature-branch
```

### 3. Switching Between Branches

```bash
# Check current environment
sprout ls

# Navigate to another environment
cd $(sprout path another-branch)
```

## Troubleshooting

### "Not in a git repository" Error
- Execute from Git repository root directory

### ".env.example file not found" Error
- Create `.env.example` in project root

### "Could not find an available port" Error
- Occurs when many ports are in use
- Stop unnecessary services

### Cannot Delete Worktree
- Process might be running in that directory
- Move out of directory and retry