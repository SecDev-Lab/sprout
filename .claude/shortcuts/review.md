# GitHub Pull Request Review (+review)

Shortcut to perform detailed review of Pull Requests in GitHub private repositories.

## Overview

This command executes comprehensive code review of specified PR and provides quality assessment and action items. Intermediate files created during review processing are placed in `tmp/` directory and automatically cleaned up after processing completion.

## Usage

```
+review <PR_URL>
```

Example:
```
+review https://github.com/owner/repo/pull/123
```

## Features

This shortcut performs the following tasks:

1. **Get PR Basic Information**
   - Get PR details with `gh pr view`
   - Title, description, reviewers, status, etc.

2. **Detailed Analysis of Code Changes**
   - Get changes with `gh pr diff`
   - Analyze change lines and content for each file

3. **Quality Review**
   - Check coding style and design patterns
   - Analyze from security and performance perspectives
   - Point out potential issues

4. **Overall Assessment and Action Items**
   - Judge whether mergeable
   - Specific improvement suggestions

5. **Intermediate File Cleanup**
   - Automatically delete intermediate files created in `tmp/` directory during review processing
   - Clean up work environment

## Prerequisites

- GitHub CLI installed (`gh` command available)
- Authenticated with `gh auth login`
- Read permission for target repository

## Execution Process

When executing shortcut, Claude Code sequentially performs:

1. Extract owner/repo/pr-number from PR URL
2. Get PR basic info with `gh pr view`
3. Get change diff with `gh pr diff`
4. Perform detailed review based on obtained data
5. Output structured review results
6. **Cleanup tmp/ directory**
   ```bash
   # Check and delete intermediate files created during review
   if [ -d "tmp/" ] && [ "$(ls -A tmp/)" ]; then
     echo "=== Intermediate files created during review processing ==="
     ls -la tmp/
     rm -rf tmp/*
     echo "Cleaned up tmp/ directory"
   fi
   ```

## Output Format

```markdown
# PR Review: [PR Title]

## Basic Information
- Repository: owner/repo
- PR Number: #XXX
- Author: [author]
- Status: [open/closed/merged]
- Changed Files: XX files
- Changes: +XXX -XXX

## Change Summary
[PR purpose and main changes]

## File-by-File Change Details
### [filename]
- Change Type: [new/modified/deleted]
- Main Changes:
  - [Specific changes]

## Code Quality Assessment
### ✅ Good Points
- [Specific evaluation points]

### ⚠️ Points for Improvement  
- [Specific improvement suggestions]

### 🚨 Potential Issues
- [Security/Performance/Bug risks]

## Overall Assessment
**Merge Decision**: [✅ APPROVE / ⚠️ REQUEST_CHANGES / 💬 COMMENT]

**Reason**: [Detailed reason for decision]

## Recommended Actions
- [ ] [Specific fix suggestions]
- [ ] [Test addition suggestions]  
- [ ] [Documentation update suggestions]
```

## Notes

- Review results are only displayed on Claude Code
- No automatic comment posting to GitHub
- Analysis may take time for large PRs
- Appropriate permissions required for private repositories
- **About tmp/ directory**:
  - Intermediate files during review processing (analysis data, temporary reports, etc.) are placed in tmp/
  - After review completion, intermediate files are automatically deleted
  - Check contents before deletion and report deletion in log output