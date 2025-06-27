"""Implementation of the create command."""

from pathlib import Path
from typing import Never

import typer
from rich.console import Console

from sprout.exceptions import SproutError
from sprout.types import BranchName
from sprout.utils import (
    branch_exists,
    ensure_sprout_dir,
    get_git_root,
    is_git_repository,
    parse_env_template,
    run_command,
    worktree_exists,
)

console = Console()


def create_worktree(branch_name: BranchName, path_only: bool = False) -> Never:
    """Create a new worktree with development environment."""
    # Check prerequisites
    if not is_git_repository():
        if not path_only:
            console.print("[red]Error: Not in a git repository[/red]")
            console.print("Please run this command from the root of a git repository.")
        else:
            typer.echo("Error: Not in a git repository", err=True)
        raise typer.Exit(1)

    git_root = get_git_root()
    env_example = git_root / ".env.example"

    if not env_example.exists():
        if not path_only:
            console.print("[red]Error: .env.example file not found[/red]")
            console.print(f"Expected at: {env_example}")
        else:
            typer.echo(f"Error: .env.example file not found at {env_example}", err=True)
        raise typer.Exit(1)

    # Check if worktree already exists
    if worktree_exists(branch_name):
        if not path_only:
            console.print(f"[red]Error: Worktree for branch '{branch_name}' already exists[/red]")
        else:
            typer.echo(f"Error: Worktree for branch '{branch_name}' already exists", err=True)
        raise typer.Exit(1)

    # Ensure .sprout directory exists
    sprout_dir = ensure_sprout_dir()
    worktree_path = sprout_dir / branch_name

    # Create the worktree
    if not path_only:
        console.print(f"Creating worktree for branch [cyan]{branch_name}[/cyan]...")

    # Check if branch exists, create if it doesn't
    if not branch_exists(branch_name):
        if not path_only:
            console.print(f"Branch '{branch_name}' doesn't exist. Creating new branch...")
        # Create branch with -b flag
        cmd = ["git", "worktree", "add", "-b", branch_name, str(worktree_path)]
    else:
        cmd = ["git", "worktree", "add", str(worktree_path), branch_name]

    try:
        run_command(cmd)
    except SproutError as e:
        if not path_only:
            console.print(f"[red]Error creating worktree: {e}[/red]")
        else:
            typer.echo(f"Error creating worktree: {e}", err=True)
        raise typer.Exit(1) from e

    # Generate .env file
    if not path_only:
        console.print("Generating .env file...")
    try:
        env_content = parse_env_template(env_example, silent=path_only)
        env_file = worktree_path / ".env"
        env_file.write_text(env_content)
    except SproutError as e:
        if not path_only:
            console.print(f"[red]Error generating .env file: {e}[/red]")
        else:
            typer.echo(f"Error generating .env file: {e}", err=True)
        # Clean up worktree on failure
        run_command(["git", "worktree", "remove", str(worktree_path)], check=False)
        raise typer.Exit(1) from e
    except KeyboardInterrupt:
        if not path_only:
            console.print("\n[yellow]Cancelled by user[/yellow]")
        else:
            typer.echo("Cancelled by user", err=True)
        # Clean up worktree on cancellation
        run_command(["git", "worktree", "remove", str(worktree_path)], check=False)
        raise typer.Exit(130) from None

    # Success message or path output
    if path_only:
        # Output only the path for shell command substitution
        print(str(worktree_path))
    else:
        console.print(f"\n[green]✅ Workspace '{branch_name}' created successfully![/green]\n")
        console.print("Navigate to your new environment with:")
        console.print(f"  [cyan]cd {worktree_path.relative_to(Path.cwd())}[/cyan]")

    # Exit successfully
    raise typer.Exit(0)
