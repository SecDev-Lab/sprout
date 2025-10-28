"""Common utilities for sprout."""

import os
import random
import re
import socket
import subprocess
from datetime import datetime
from pathlib import Path
from typing import TypeAlias

import typer
from rich.console import Console

from sprout.exceptions import SproutError
from sprout.types import BranchName, WorktreeInfo

# Type aliases
PortNumber: TypeAlias = int
PortSet: TypeAlias = set[PortNumber]

console = Console()


def is_git_repository() -> bool:
    """Check if current directory is inside a git repository."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            capture_output=True,
            text=True,
            check=False,
        )
        return result.returncode == 0
    except (subprocess.SubprocessError, FileNotFoundError):
        return False


def get_git_root() -> Path:
    """Get the root directory of the git repository."""
    if not is_git_repository():
        raise SproutError("Not in a git repository")

    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
        check=True,
    )
    return Path(result.stdout.strip())


def run_command(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess[str]:
    """Run a command and return the result."""
    try:
        return subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=check,
        )
    except subprocess.CalledProcessError as e:
        raise SproutError(f"Command failed: {' '.join(cmd)}\n{e.stderr}") from e


def get_sprout_dir() -> Path:
    """Get the .sprout directory path."""
    return get_git_root() / ".sprout"


def ensure_sprout_dir() -> Path:
    """Ensure .sprout directory exists and return its path."""
    sprout_dir = get_sprout_dir()
    sprout_dir.mkdir(exist_ok=True)
    return sprout_dir


def get_used_ports() -> PortSet:
    """Get all ports currently used by sprout worktrees."""
    used_ports: PortSet = set()
    sprout_dir = get_sprout_dir()

    if not sprout_dir.exists():
        return used_ports

    # Scan all .env files recursively in .sprout/
    for env_file in sprout_dir.rglob("*.env"):
        if env_file.is_file():
            try:
                content = env_file.read_text()
                # Find all port assignments (e.g., PORT=8080)
                port_matches = re.findall(r"=(\d{4,5})\b", content)
                for port_str in port_matches:
                    port = int(port_str)
                    if 1024 <= port <= 65535:
                        used_ports.add(port)
            except (OSError, ValueError):
                continue

    return used_ports


def is_port_available(port: PortNumber) -> bool:
    """Check if a port is available for binding."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        try:
            sock.bind(("127.0.0.1", port))
            return True
        except OSError:
            return False


def find_available_port() -> PortNumber:
    """Find an available port that's not used by sprout or system."""
    used_ports = get_used_ports()
    max_attempts = 1000

    for _ in range(max_attempts):
        # Random port between 1024 and 65535
        port = random.randint(1024, 65535)

        if port not in used_ports and is_port_available(port):
            return port

    raise SproutError("Could not find an available port after 1000 attempts")


def parse_env_template(
    template_path: Path,
    silent: bool = False,
    used_ports: PortSet | None = None,
    branch_name: str | None = None,
) -> str:
    """Parse .env.example template and process placeholders.

    Args:
        template_path: Path to the .env.example template file
        silent: If True, use stderr for prompts to keep stdout clean
        used_ports: Set of ports already in use (in addition to system-wide used ports)
        branch_name: Branch name to use for {{ branch() }} placeholders
    """
    if not template_path.exists():
        raise SproutError(f".env.example file not found at {template_path}")

    try:
        content = template_path.read_text()
    except OSError as e:
        raise SproutError(f"Failed to read .env.example: {e}") from e

    lines: list[str] = []
    # Track used ports within this file to avoid duplicates
    file_ports: PortSet = set()
    # Include any additional used ports passed in
    if used_ports:
        file_ports.update(used_ports)

    for line in content.splitlines():
        # Process {{ auto_port() | default }} placeholders
        def replace_auto_port(match: re.Match[str]) -> str:
            # Extract default value if present (group 1)
            default_value = match.group(1)
            if default_value is not None:
                default_value = default_value.strip()

            # Generate available port
            port = find_available_port()
            while port in file_ports:
                port = find_available_port()
            file_ports.add(port)
            return str(port)

        line = re.sub(r"{{\s*auto_port\(\)(?:\s*\|\s*([^}]*))?\s*}}", replace_auto_port, line)

        # Process {{ branch() | default }} placeholders
        def replace_branch(match: re.Match[str]) -> str:
            # Extract default value if present (group 1)
            default_value = match.group(1)
            if default_value is not None:
                default_value = default_value.strip()

            # Use branch_name if provided, otherwise use default
            if branch_name:
                return branch_name
            elif default_value is not None:
                return default_value
            else:
                # No branch name and no default - keep placeholder unchanged
                return match.group(0)

        line = re.sub(r"{{\s*branch\(\)(?:\s*\|\s*([^}]*))?\s*}}", replace_branch, line)

        # Process {{ VARIABLE | default }} placeholders
        def replace_variable(match: re.Match[str]) -> str:
            var_name = match.group(1).strip()
            # Extract default value if present (group 2)
            default_value = match.group(2)
            if default_value is not None:
                default_value = default_value.strip()

            # Check environment variable first
            value = os.environ.get(var_name)
            if value is None:
                # If default value is provided, use it
                if default_value is not None:
                    return default_value

                # No default value - prompt user for value
                # Create a relative path for display
                try:
                    display_path = template_path.relative_to(Path.cwd())
                except ValueError:
                    display_path = template_path

                # Prompt user for value with file context
                if silent:
                    # Use stderr for prompts in silent mode to keep stdout clean
                    prompt = f"Enter a value for '{var_name}' (from {display_path}): "
                    typer.echo(prompt, err=True, nl=False)
                    value = input()
                else:
                    prompt = (
                        f"Enter a value for '[cyan]{var_name}[/cyan]' "
                        f"(from [dim]{display_path}[/dim]): "
                    )
                    value = console.input(prompt)
            return value

        # Only match variables that don't look like function calls (no parentheses)
        # Now also captures optional | default_value
        line = re.sub(r"{{\s*([^}()]+?)(?:\s*\|\s*([^}]*))?\s*}}", replace_variable, line)

        lines.append(line)

    return "\n".join(lines)


def worktree_exists(branch_name: BranchName) -> bool:
    """Check if a worktree already exists for the given branch."""
    worktree_path = get_sprout_dir() / branch_name
    return worktree_path.exists()


def branch_exists(branch_name: BranchName) -> bool:
    """Check if a git branch exists."""
    result = run_command(["git", "rev-parse", "--verify", f"refs/heads/{branch_name}"], check=False)
    return result.returncode == 0


def get_indexed_worktrees() -> list[WorktreeInfo]:
    """Get a list of sprout-managed worktrees with consistent ordering.

    Returns:
        List of WorktreeInfo dicts, sorted by branch name for consistent indexing.
    """
    if not is_git_repository():
        raise SproutError("Not in a git repository")

    sprout_dir = get_sprout_dir()

    # Get worktree list from git
    result = run_command(["git", "worktree", "list", "--porcelain"])

    # Parse worktree output
    worktrees: list[WorktreeInfo] = []
    current_worktree: WorktreeInfo = {}

    for line in result.stdout.strip().split("\n"):
        if not line:
            if current_worktree:
                worktrees.append(current_worktree)
                current_worktree = {}
            continue

        if line.startswith("worktree "):
            current_worktree["path"] = Path(line[9:])
        elif line.startswith("branch "):
            branch_ref = line[7:]
            # Strip refs/heads/ prefix if present
            if branch_ref.startswith("refs/heads/"):
                current_worktree["branch"] = branch_ref[11:]
            else:
                current_worktree["branch"] = branch_ref
        elif line.startswith("HEAD "):
            current_worktree["head"] = line[5:]

    if current_worktree:
        worktrees.append(current_worktree)

    # Filter for sprout-managed worktrees
    sprout_worktrees: list[WorktreeInfo] = []
    current_path = Path.cwd().resolve()

    for wt in worktrees:
        wt_path = wt["path"].resolve()
        if wt_path.parent == sprout_dir:
            # Check if we're currently in this worktree
            wt["is_current"] = current_path == wt_path or current_path.is_relative_to(wt_path)

            # Get last modified time
            if wt_path.exists():
                stat = wt_path.stat()
                wt["modified"] = datetime.fromtimestamp(stat.st_mtime)
            else:
                wt["modified"] = None

            sprout_worktrees.append(wt)

    # Sort by branch name for consistent indexing
    sprout_worktrees.sort(key=lambda wt: wt.get("branch") or wt.get("head") or "")

    return sprout_worktrees


def resolve_branch_identifier(identifier: str) -> BranchName | None:
    """Resolve a branch identifier (name or index) to a branch name.

    Args:
        identifier: Either a branch name or a 1-based index number

    Returns:
        Branch name if found, None otherwise
    """
    # Check if identifier is a number
    if identifier.isdigit():
        index = int(identifier)
        worktrees = get_indexed_worktrees()

        if 1 <= index <= len(worktrees):
            return worktrees[index - 1].get("branch", worktrees[index - 1].get("head", ""))
        return None

    # Otherwise treat as branch name
    return identifier
