# +brc - Branch Review & Cleanup

Reviews differences between current branch and main branch, and performs branch cleanup.

## Overview

This command comprehensively executes quality checks and cleanup before PR creation. It focuses on:

- Ensuring code quality (lint, format)
- Removing unnecessary files and code
- **Complete cleanup of tmp/ directory**
- TODO review and resolution
- Test success confirmation

## Execution Steps

### 1. Diff Confirmation
```bash
git diff main...HEAD
git diff --name-only main...HEAD
```
Confirms files changed in current branch and their contents.

### 2. Remove Unnecessary Files and Code Fragments
- Remove debug print statements, console.log, temporary comment-outs
- Remove temporary test files (test_*.py, *.log, *.tmp etc.) not used in actual tests
- Remove unused import statements
- Remove experimental code used only during implementation
- **tmp/ directory cleanup**:
  ```bash
  # Check tmp/ directory contents
  if [ -d "tmp/" ]; then
    echo "=== tmp/ directory contents ==="
    ls -la tmp/
    echo "Delete these files? (y/N)"
    # Wait for user confirmation
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
      rm -rf tmp/*
      echo "Cleaned up tmp/ directory"
    fi
  else
    echo "tmp/ directory does not exist"
  fi
  ```

### 3. TODO Review and Resolution
```bash
# Search for TODO comments
rg "TODO|FIXME|XXX|HACK" --type-add 'code:*.{py,ts,js,tsx,jsx}' -t code
```
- Check each TODO found
- Immediately resolve items that should be resolved in current branch
- For items to keep as future tasks, clearly state reason in summary

### 4. Format Fixes
```bash
make format
make lint
```
- If lint errors exist, check error messages and fix
- Manually fix errors that cannot be auto-fixed

### 5. Test Fixes
```bash
make test
```
- If tests fail:
  - First analyze error messages
  - Confirm if test expectations are correct
  - Determine whether to fix implementation or tests
  - If prioritizing implementation over tests, state reason in summary

### 6. Final Confirmation and Summary Display
Display summary in the following format:

```
## Branch Review Summary

### Changes
- Changed files: X files
- Added lines: +XXX
- Deleted lines: -XXX

### Cleanup Performed
- [ ] Removed unnecessary debug code
- [ ] Removed unused imports
- [ ] Removed temporary files
- [ ] Cleaned up tmp/ directory

### TODO Status
- Resolved: X items
- Remaining: X items
  - [Reason] TODO content

### Test & Quality Check
- [ ] make format: PASS/FAIL
- [ ] make lint: PASS/FAIL  
- [ ] make test: PASS/FAIL

### Remaining Issues
(List if any)

### Next Steps
(If all checks PASS)
Ready to create PR. Use the following command to create a PR:
gh pr create --title "Title" --body "Description"
```

## Notes
- Carefully judge unnecessary code to not damage implementation intent
- When tests fail, don't hastily fix tests, prioritize verifying implementation correctness
- Don't automatically create PR, prompt for user's final confirmation
- **About tmp/ directory**:
  - All intermediate files created by Claude Code (test files, planning documents, etc.) are placed in tmp/
  - Always perform cleanup when executing +brc
  - Request user confirmation before deletion