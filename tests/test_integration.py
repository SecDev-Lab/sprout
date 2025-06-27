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

    # Get the default branch name
    result = subprocess.run(
        ["git", "branch", "--show-current"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=True,
    )
    default_branch = result.stdout.strip()

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

    return tmp_path, default_branch


class TestIntegrationWorkflow:
    """Test complete workflows."""

    def test_placeholder_substitution_from_env(self, git_repo, monkeypatch):
        """Test that placeholders in .env.example are correctly substituted from environment variables."""
        git_repo, default_branch = git_repo
        monkeypatch.chdir(git_repo)
        
        # Set multiple environment variables
        monkeypatch.setenv("API_KEY", "test_api_key_123")
        monkeypatch.setenv("DATABASE_URL", "postgres://localhost/test")
        
        # Create .env.example with various placeholder patterns
        env_example = git_repo / ".env.example"
        env_example.write_text(
            "# Test environment file\n"
            "API_KEY={{ API_KEY }}\n"
            "DATABASE_URL={{ DATABASE_URL }}\n"
            "SECRET_TOKEN={{ SECRET_TOKEN }}\n"  # Not in env, should prompt
            "WEB_PORT={{ auto_port() }}\n"
            "STATIC_VAR=fixed_value\n"
            "COMPOSE_VAR=${COMPOSE_VAR:-default}\n"
        )
        
        # Create worktree - SECRET_TOKEN should be prompted but we can't test that
        # So let's set it too
        monkeypatch.setenv("SECRET_TOKEN", "secret123")
        result = runner.invoke(app, ["create", "test-branch"])
        assert result.exit_code == 0
        
        # Verify .env was created with correct substitutions
        env_file = git_repo / ".sprout" / "test-branch" / ".env"
        env_content = env_file.read_text()
        
        # Check environment variable substitutions
        assert "API_KEY=test_api_key_123" in env_content
        assert "DATABASE_URL=postgres://localhost/test" in env_content
        assert "SECRET_TOKEN=secret123" in env_content
        assert "STATIC_VAR=fixed_value" in env_content
        assert "COMPOSE_VAR=${COMPOSE_VAR:-default}" in env_content
        assert "WEB_PORT=" in env_content  # Should have a port number

    def test_create_with_env_variables(self, git_repo, monkeypatch):
        """Test creating worktree with environment variables."""
        git_repo, default_branch = git_repo
        monkeypatch.chdir(git_repo)
        monkeypatch.setenv("API_KEY", "test_api_key")

        # Create worktree
        result = runner.invoke(app, ["create", "feature-branch"])
        assert result.exit_code == 0
        assert "✅ Workspace 'feature-branch' created successfully!" in result.stdout

        # Verify worktree was created
        worktree_path = git_repo / ".sprout" / "feature-branch"
        assert worktree_path.exists()

        # Verify .env was created with proper values from environment
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

    def test_list_and_path_commands(self, git_repo, monkeypatch):
        """Test listing worktrees and getting paths."""
        git_repo, default_branch = git_repo
        monkeypatch.chdir(git_repo)
        monkeypatch.setenv("API_KEY", "test_key")

        # Create a worktree first
        result = runner.invoke(app, ["create", "feature-branch"])
        assert result.exit_code == 0

        worktree_path = git_repo / ".sprout" / "feature-branch"

        # List worktrees
        result = runner.invoke(app, ["ls"])
        assert result.exit_code == 0
        assert "feature-branch" in result.stdout

        # Get path
        result = runner.invoke(app, ["path", "feature-branch"])
        assert result.exit_code == 0
        assert str(worktree_path) in result.stdout

    def test_create_existing_branch(self, git_repo, monkeypatch):
        """Test creating worktree for existing branch."""
        git_repo, default_branch = git_repo
        monkeypatch.chdir(git_repo)
        monkeypatch.setenv("API_KEY", "test_key")

        # Create a branch first
        subprocess.run(
            ["git", "checkout", "-b", "existing-branch"],
            cwd=git_repo,
            check=True,
        )
        subprocess.run(
            ["git", "checkout", default_branch],
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
        git_repo, default_branch = git_repo
        monkeypatch.chdir(git_repo)
        monkeypatch.setenv("API_KEY", "test_key")

        # Create worktree first
        result = runner.invoke(app, ["create", "test-branch"])
        assert result.exit_code == 0

        # Try to create same worktree again
        result = runner.invoke(app, ["create", "test-branch"])
        assert result.exit_code == 1
        assert "already exists" in result.stdout

        # Try to remove non-existent worktree - now just test the error message
        # without the actual removal since we removed stdin prompts
        from sprout.utils import worktree_exists
        assert not worktree_exists("nonexistent")

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
