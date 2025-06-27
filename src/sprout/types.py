"""Type definitions for sprout."""

from datetime import datetime
from pathlib import Path
from typing import TypeAlias, TypedDict

# Type aliases
BranchName: TypeAlias = str
WorktreePath: TypeAlias = Path
EnvContent: TypeAlias = str


class WorktreeInfo(TypedDict, total=False):
    """Information about a git worktree."""

    path: Path
    branch: str | None
    head: str | None
    is_current: bool
    modified: datetime | None


class GitWorktreeOutput(TypedDict):
    """Parsed output from git worktree list."""

    path: Path
    branch: str | None
    head: str | None
