"""Implementation of the rm command."""

import typer
from rich.console import Console
from rich.prompt import Confirm

from sprout.exceptions import SproutError
from sprout.utils import (
    get_sprout_dir,
    is_git_repository,
    run_command,
    worktree_exists,
)

console = Console()


def remove_worktree(branch_name: str) -> None:
    """Remove a development environment."""
    if not is_git_repository():
        console.print("[red]Error: Not in a git repository[/red]")
        raise typer.Exit(1)

    # Check if worktree exists
    if not worktree_exists(branch_name):
        console.print(f"[red]Error: Worktree for branch '{branch_name}' does not exist[/red]")
        raise typer.Exit(1)

    worktree_path = get_sprout_dir() / branch_name

    # Confirm removal
    if not Confirm.ask(
        f"Are you sure you want to remove the worktree for branch '[cyan]{branch_name}[/cyan]'?"
    ):
        console.print("[yellow]Cancelled[/yellow]")
        raise typer.Exit(0)

    # Remove worktree
    console.print(f"Removing worktree for branch [cyan]{branch_name}[/cyan]...")
    try:
        run_command(["git", "worktree", "remove", str(worktree_path)])
        console.print("[green]✅ Worktree removed successfully[/green]")
    except SproutError as e:
        console.print(f"[red]Error removing worktree: {e}[/red]")
        raise typer.Exit(1) from e

    # Ask about branch deletion
    if Confirm.ask(f"Do you also want to delete the git branch '[cyan]{branch_name}[/cyan]'?"):
        try:
            # Try normal deletion first
            result = run_command(["git", "branch", "-d", branch_name], check=False)
            if result.returncode != 0:
                # If normal deletion fails, show the error and ask about force delete
                console.print(f"[yellow]Warning: {result.stderr.strip()}[/yellow]")
                if Confirm.ask("Force delete the branch?"):
                    run_command(["git", "branch", "-D", branch_name])
                    console.print("[green]✅ Branch deleted successfully[/green]")
                else:
                    console.print("[yellow]Branch deletion cancelled[/yellow]")
            else:
                console.print("[green]✅ Branch deleted successfully[/green]")
        except SproutError as e:
            console.print(f"[red]Error deleting branch: {e}[/red]")
            console.print(
                "[yellow]Note: The worktree has been removed, but the branch still exists[/yellow]"
            )
