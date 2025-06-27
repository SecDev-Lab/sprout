"""Integration tests for sprout."""

import subprocess
from pathlib import Path

import pytest
from typer.testing import CliRunner

from sprout.cli import app

runner = CliRunner()


@pytest.fixture
def git_repo(tmp_path):
    """Create a temporary git repository for testing."""
    # Initialize git repo
    subprocess.run(["git", "init"], cwd=tmp_path, check=True)
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=tmp_path,
        check=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=tmp_path,
        check=True,
    )

    # Create initial commit
    (tmp_path / "README.md").write_text("# Test Project")
    subprocess.run(["git", "add", "."], cwd=tmp_path, check=True)
    subprocess.run(
        ["git", "commit", "-m", "Initial commit"],
        cwd=tmp_path,
        check=True,
    )
    
    # Ensure we're on a branch named 'main'
    # First check current branch name
    result = subprocess.run(
        ["git", "branch", "--show-current"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=True,
    )
    current_branch = result.stdout.strip()
    
    # If not on 'main', rename the branch
    if current_branch != "main":
        subprocess.run(
            ["git", "branch", "-m", current_branch, "main"],
            cwd=tmp_path,
            check=True,
        )

    # Create .env.example
    env_example = tmp_path / ".env.example"
    env_example.write_text(
        "# Example environment file\n"
        "API_KEY={{ API_KEY }}\n"
        "WEB_PORT={{ auto_port() }}\n"
        "DB_PORT={{ auto_port() }}\n"
        "STATIC_VAR=fixed_value\n"
        "COMPOSE_VAR=${COMPOSE_VAR:-default}\n"
    )

    return tmp_path


class TestIntegrationWorkflow:
    """Test complete workflows."""

    def test_create_list_remove_workflow(self, git_repo, monkeypatch):
        """Test creating, listing, and removing a worktree."""
        monkeypatch.chdir(git_repo)
        monkeypatch.setenv("API_KEY", "test_api_key")

        # Create worktree
        result = runner.invoke(app, ["create", "feature-branch"])
        assert result.exit_code == 0
        assert "✅ Workspace 'feature-branch' created successfully!" in result.stdout

        # Verify worktree was created
        worktree_path = git_repo / ".sprout" / "feature-branch"
        assert worktree_path.exists()

        # Verify .env was created with proper values
        env_file = worktree_path / ".env"
        assert env_file.exists()
        env_content = env_file.read_text()
        assert "API_KEY=test_api_key" in env_content
        assert "WEB_PORT=" in env_content
        assert "DB_PORT=" in env_content
        assert "STATIC_VAR=fixed_value" in env_content
        assert "COMPOSE_VAR=${COMPOSE_VAR:-default}" in env_content

        # Extract ports to verify they're different
        lines = env_content.splitlines()
        web_port = None
        db_port = None
        for line in lines:
            if line.startswith("WEB_PORT="):
                web_port = int(line.split("=")[1])
            elif line.startswith("DB_PORT="):
                db_port = int(line.split("=")[1])

        assert web_port is not None
        assert db_port is not None
        assert web_port != db_port
        assert 1024 <= web_port <= 65535
        assert 1024 <= db_port <= 65535

        # List worktrees
        result = runner.invoke(app, ["ls"])
        assert result.exit_code == 0
        assert "feature-branch" in result.stdout

        # Get path
        result = runner.invoke(app, ["path", "feature-branch"])
        assert result.exit_code == 0
        assert str(worktree_path) in result.stdout

        # Remove worktree (with --yes flag to skip prompts in test)
        result = runner.invoke(app, ["rm", "feature-branch"], input="y\nn\n")
        assert result.exit_code == 0
        assert "✅ Worktree removed successfully" in result.stdout

        # Verify worktree was removed
        assert not worktree_path.exists()

    def test_create_with_user_input(self, git_repo, monkeypatch):
        """Test creating worktree with user input for variables."""
        monkeypatch.chdir(git_repo)

        # Simulate user input for API_KEY
        result = runner.invoke(
            app,
            ["create", "dev-branch"],
            input="user_provided_key\n",
        )

        assert result.exit_code == 0

        # Verify .env contains user-provided value
        env_file = git_repo / ".sprout" / "dev-branch" / ".env"
        env_content = env_file.read_text()
        assert "API_KEY=user_provided_key" in env_content

    def test_create_existing_branch(self, git_repo, monkeypatch):
        """Test creating worktree for existing branch."""
        monkeypatch.chdir(git_repo)
        monkeypatch.setenv("API_KEY", "test_key")

        # Create a branch first
        subprocess.run(
            ["git", "checkout", "-b", "existing-branch"],
            cwd=git_repo,
            check=True,
        )
        subprocess.run(
            ["git", "checkout", "main"],
            cwd=git_repo,
            check=True,
        )

        # Create worktree for existing branch
        result = runner.invoke(app, ["create", "existing-branch"])
        assert result.exit_code == 0

        worktree_path = git_repo / ".sprout" / "existing-branch"
        assert worktree_path.exists()

    def test_error_cases(self, git_repo, monkeypatch, tmp_path):
        """Test various error conditions."""
        monkeypatch.chdir(git_repo)
        monkeypatch.setenv("API_KEY", "test_key")

        # Create worktree first
        result = runner.invoke(app, ["create", "test-branch"])
        assert result.exit_code == 0

        # Try to create same worktree again
        result = runner.invoke(app, ["create", "test-branch"])
        assert result.exit_code == 1
        assert "already exists" in result.stdout

        # Try to remove non-existent worktree
        result = runner.invoke(app, ["rm", "nonexistent"])
        assert result.exit_code == 1
        assert "does not exist" in result.stdout

        # Try to get path of non-existent worktree
        result = runner.invoke(app, ["path", "nonexistent"])
        assert result.exit_code == 1

        # Remove .env.example and try to create
        (git_repo / ".env.example").unlink()
        result = runner.invoke(app, ["create", "another-branch"])
        assert result.exit_code == 1
        assert ".env.example file not found" in result.stdout

        # Test outside git repo using a separate temp directory
        import tempfile

        with tempfile.TemporaryDirectory() as non_git_tmpdir:
            non_git_dir = Path(non_git_tmpdir) / "not-a-repo"
            non_git_dir.mkdir()
            monkeypatch.chdir(non_git_dir)

            result = runner.invoke(app, ["create", "branch"])
            assert result.exit_code == 1
            assert "Not in a git repository" in result.stdout
