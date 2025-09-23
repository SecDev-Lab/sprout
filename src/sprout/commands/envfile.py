"""Environment file management command implementation."""

import subprocess
from pathlib import Path
from typing import TypeAlias

from rich.console import Console
from rich.table import Table

from sprout.exceptions import SproutError
from sprout.utils import get_used_ports, parse_env_template

PortSet: TypeAlias = set[int]

console = Console()


def get_current_branch() -> str | None:
    """Get the current git branch name."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0:
            branch = result.stdout.strip()
            if branch != "HEAD":
                return branch
    except (subprocess.SubprocessError, FileNotFoundError):
        pass
    return None


def find_env_example_files(root_dir: Path) -> list[Path]:
    """Find all .env.example files recursively from the given directory."""
    return sorted(root_dir.rglob(".env.example"))


def create_env_files(
    force: bool = False,
    dry_run: bool = False,
    silent: bool = False,
) -> None:
    """Create .env files from .env.example templates in current directory and subdirectories.

    Args:
        force: Overwrite existing .env files
        dry_run: Show what would be created without creating files
        silent: Suppress output except for prompts
    """
    root_dir = Path.cwd()
    env_examples = find_env_example_files(root_dir)

    if not env_examples:
        if not silent:
            console.print(
                "[yellow]No .env.example files found in current directory "
                "or subdirectories[/yellow]"
            )
        return

    branch_name = get_current_branch()
    used_ports = get_used_ports()

    created_files: list[tuple[Path, str]] = []
    skipped_files: list[tuple[Path, str]] = []
    errors: list[tuple[Path, str]] = []

    if not silent:
        console.print(f"[cyan]Found {len(env_examples)} .env.example file(s)[/cyan]")
        if branch_name:
            console.print(f"[dim]Current branch: {branch_name}[/dim]")
        console.print()

    for example_path in env_examples:
        env_path = example_path.parent / ".env"

        try:
            relative_env = env_path.relative_to(root_dir)
        except ValueError:
            relative_env = env_path

        if env_path.exists() and not force:
            skipped_files.append((relative_env, "already exists"))
            if not silent:
                console.print(f"[dim]Skipping {relative_env} (already exists)[/dim]")
            continue

        if dry_run:
            if env_path.exists():
                created_files.append((relative_env, "would overwrite"))
            else:
                created_files.append((relative_env, "would create"))
            if not silent:
                action = "Would overwrite" if env_path.exists() else "Would create"
                console.print(f"[blue]{action}[/blue] {relative_env}")
            continue

        try:
            parsed_content = parse_env_template(
                example_path,
                silent=silent,
                used_ports=used_ports,
                branch_name=branch_name,
            )

            env_path.write_text(parsed_content)

            if env_path.exists() and force:
                created_files.append((relative_env, "overwritten"))
                if not silent:
                    console.print(f"[green]✓[/green] Overwritten {relative_env}")
            else:
                created_files.append((relative_env, "created"))
                if not silent:
                    console.print(f"[green]✓[/green] Created {relative_env}")

        except SproutError as e:
            errors.append((relative_env, str(e)))
            if not silent:
                console.print(f"[red]✗[/red] Failed to create {relative_env}: {e}")
        except Exception as e:
            errors.append((relative_env, f"Unexpected error: {e}"))
            if not silent:
                console.print(
                    f"[red]✗[/red] Failed to create {relative_env}: Unexpected error: {e}"
                )

    if not silent:
        console.print()
        _show_summary(created_files, skipped_files, errors, dry_run)


def _show_summary(
    created_files: list[tuple[Path, str]],
    skipped_files: list[tuple[Path, str]],
    errors: list[tuple[Path, str]],
    dry_run: bool,
) -> None:
    """Show summary of the operation."""
    table = Table(title="Summary", show_header=True, header_style="bold cyan")
    table.add_column("Status", style="cyan", no_wrap=True)
    table.add_column("Count", justify="right")

    if dry_run:
        would_create = len([f for f in created_files if f[1] == "would create"])
        would_overwrite = len([f for f in created_files if f[1] == "would overwrite"])
        if would_create:
            table.add_row("Would create", str(would_create))
        if would_overwrite:
            table.add_row("Would overwrite", str(would_overwrite))
    else:
        created = len([f for f in created_files if f[1] == "created"])
        overwritten = len([f for f in created_files if f[1] == "overwritten"])
        if created:
            table.add_row("Created", str(created))
        if overwritten:
            table.add_row("Overwritten", str(overwritten))

    if skipped_files:
        table.add_row("Skipped", str(len(skipped_files)))

    if errors:
        table.add_row("[red]Failed[/red]", str(len(errors)))

    console.print(table)

