"""Implementation of the path command."""

import typer

from sprout.utils import get_sprout_dir, is_git_repository, worktree_exists

console = typer.get_text_stream("stdout")


def get_worktree_path(branch_name: str) -> None:
    """Get the path of a development environment."""
    if not is_git_repository():
        typer.echo("Error: Not in a git repository", err=True)
        raise typer.Exit(1)

    # Check if worktree exists
    if not worktree_exists(branch_name):
        typer.echo(f"Error: Worktree for branch '{branch_name}' does not exist", err=True)
        raise typer.Exit(1)

    worktree_path = get_sprout_dir() / branch_name

    # Output only the path, no extra formatting
    print(str(worktree_path))
