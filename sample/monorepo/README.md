# Sample Monorepo for Sprout Testing

This directory contains a sample monorepo structure to demonstrate sprout's multiple `.env.example` file support.

## Structure

```
sample/monorepo/
├── .env.example              # Root configuration (database, redis, common settings)
├── docker-compose.yml        # Multi-service Docker setup
├── frontend/
│   └── .env.example         # Frontend-specific environment variables
├── backend/
│   └── .env.example         # Backend API configuration
└── shared/
    └── .env.example         # Shared utilities configuration
```

## Environment Variables Required

Before testing, set these environment variables:

```bash
export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/myapp"
export REACT_APP_API_KEY="your-frontend-api-key"
export JWT_SECRET="your-jwt-secret-key"
export SMTP_USER="your-smtp-username"
export SMTP_PASS="your-smtp-password"
```

## Testing with Sprout

1. Navigate to this directory:
   ```bash
   cd sample/monorepo
   ```

2. Initialize as a git repository (if not already):
   ```bash
   git init
   git add .
   git commit -m "Initial monorepo setup"
   ```

3. Create a sprout worktree:
   ```bash
   sprout create feature-test
   ```

4. Navigate to the created worktree:
   ```bash
   cd .sprout/feature-test
   ```

5. Verify all `.env` files were created with unique ports:
   ```bash
   find . -name "*.env" -exec echo "=== {} ===" \; -exec cat {} \;
   ```

6. Start the services:
   ```bash
   docker-compose up -d
   ```

## Expected Behavior

- Sprout should detect all 4 `.env.example` files
- Each `{{ auto_port() }}` should get a unique port number
- All `.env` files should be created in their respective directories
- No port conflicts should occur when running multiple worktrees