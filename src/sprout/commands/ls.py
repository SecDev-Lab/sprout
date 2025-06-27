"""Implementation of the ls command."""

import typer
from rich.console import Console
from rich.table import Table

from sprout.utils import get_indexed_worktrees, is_git_repository

console = Console()


def list_worktrees() -> None:
    """List all managed development environments."""
    if not is_git_repository():
        console.print("[red]Error: Not in a git repository[/red]")
        raise typer.Exit(1)

    try:
        sprout_worktrees = get_indexed_worktrees()
    except Exception as e:
        console.print(f"[red]Error listing worktrees: {e}[/red]")
        raise typer.Exit(1) from e

    if not sprout_worktrees:
        console.print("[yellow]No sprout-managed worktrees found.[/yellow]")
        console.print("Use 'sprout create <branch-name>' to create one.")
        return None

    # Create table with index column
    table = Table(title="Sprout Worktrees", show_lines=True)
    table.add_column("No.", style="bright_white", no_wrap=True, width=4)
    table.add_column("Branch", style="cyan", no_wrap=True)
    table.add_column("Path", style="blue")
    table.add_column("Status", style="green")
    table.add_column("Last Modified", style="yellow")

    from pathlib import Path

    for idx, wt in enumerate(sprout_worktrees, 1):
        branch = wt.get("branch", wt.get("head", "detached"))
        path = str(wt["path"].relative_to(Path.cwd()))
        status = "[green]● current[/green]" if wt.get("is_current", False) else ""
        modified_dt = wt.get("modified")
        modified = modified_dt.strftime("%Y-%m-%d %H:%M") if modified_dt else "N/A"

        table.add_row(str(idx), branch, path, status, modified)

    console.print(table)
