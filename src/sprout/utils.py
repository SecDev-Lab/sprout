"""Common utilities for sprout."""

import os
import random
import re
import socket
import subprocess
from pathlib import Path
from typing import Set

from rich.console import Console

from sprout.exceptions import SproutError

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


def run_command(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
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


def get_used_ports() -> Set[int]:
    """Get all ports currently used by sprout worktrees."""
    used_ports = set()
    sprout_dir = get_sprout_dir()

    if not sprout_dir.exists():
        return used_ports

    # Scan all .env files in .sprout/*/
    for env_file in sprout_dir.glob("*/.env"):
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


def is_port_available(port: int) -> bool:
    """Check if a port is available for binding."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        try:
            sock.bind(("127.0.0.1", port))
            return True
        except OSError:
            return False


def find_available_port() -> int:
    """Find an available port that's not used by sprout or system."""
    used_ports = get_used_ports()
    max_attempts = 1000

    for _ in range(max_attempts):
        # Random port between 1024 and 65535
        port = random.randint(1024, 65535)

        if port not in used_ports and is_port_available(port):
            return port

    raise SproutError("Could not find an available port after 1000 attempts")


def parse_env_template(template_path: Path) -> str:
    """Parse .env.example template and process placeholders."""
    if not template_path.exists():
        raise SproutError(f".env.example file not found at {template_path}")

    try:
        content = template_path.read_text()
    except OSError as e:
        raise SproutError(f"Failed to read .env.example: {e}") from e

    lines = []
    # Track used ports within this file to avoid duplicates
    file_ports = set()

    for line in content.splitlines():
        # Process {{ auto_port() }} placeholders
        def replace_auto_port(match: re.Match) -> str:
            port = find_available_port()
            while port in file_ports:
                port = find_available_port()
            file_ports.add(port)
            return str(port)

        line = re.sub(r"{{\s*auto_port\(\)\s*}}", replace_auto_port, line)

        # Process {{ VARIABLE }} placeholders
        def replace_variable(match: re.Match) -> str:
            var_name = match.group(1).strip()
            # Check environment variable first
            value = os.environ.get(var_name)
            if value is None:
                # Prompt user for value
                value = console.input(f"Enter a value for '{var_name}': ")
            return value

        line = re.sub(r"{{\s*([^}]+)\s*}}", replace_variable, line)

        lines.append(line)

    return "\n".join(lines)


def worktree_exists(branch_name: str) -> bool:
    """Check if a worktree already exists for the given branch."""
    worktree_path = get_sprout_dir() / branch_name
    return worktree_path.exists()


def branch_exists(branch_name: str) -> bool:
    """Check if a git branch exists."""
    result = run_command(["git", "rev-parse", "--verify", f"refs/heads/{branch_name}"], check=False)
    return result.returncode == 0
