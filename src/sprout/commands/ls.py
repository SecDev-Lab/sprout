"""Implementation of the ls command."""

from datetime import datetime
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from sprout.exceptions import SproutError
from sprout.utils import get_sprout_dir, is_git_repository, run_command

console = Console()


def list_worktrees() -> None:
    """List all managed development environments."""
    if not is_git_repository():
        console.print("[red]Error: Not in a git repository[/red]")
        raise typer.Exit(1)

    sprout_dir = get_sprout_dir()

    # Get worktree list from git
    try:
        result = run_command(["git", "worktree", "list", "--porcelain"])
    except SproutError as e:
        console.print(f"[red]Error listing worktrees: {e}[/red]")
        raise typer.Exit(1) from e

    # Parse worktree output
    worktrees = []
    current_worktree = {}

    for line in result.stdout.strip().split("\n"):
        if not line:
            if current_worktree:
                worktrees.append(current_worktree)
                current_worktree = {}
            continue

        if line.startswith("worktree "):
            current_worktree["path"] = Path(line[9:])
        elif line.startswith("branch "):
            current_worktree["branch"] = line[7:]
        elif line.startswith("HEAD "):
            current_worktree["head"] = line[5:]

    if current_worktree:
        worktrees.append(current_worktree)

    # Filter for sprout-managed worktrees
    sprout_worktrees = []
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

    if not sprout_worktrees:
        console.print("[yellow]No sprout-managed worktrees found.[/yellow]")
        console.print("Use 'sprout create <branch-name>' to create one.")
        return

    # Create table
    table = Table(title="Sprout Worktrees", show_lines=True)
    table.add_column("Branch", style="cyan", no_wrap=True)
    table.add_column("Path", style="blue")
    table.add_column("Status", style="green")
    table.add_column("Last Modified", style="yellow")

    for wt in sprout_worktrees:
        branch = wt.get("branch", wt.get("head", "detached"))
        path = str(wt["path"].relative_to(Path.cwd()))
        status = "[green]● current[/green]" if wt["is_current"] else ""
        modified = wt["modified"].strftime("%Y-%m-%d %H:%M") if wt["modified"] else "N/A"

        table.add_row(branch, path, status, modified)

    console.print(table)
