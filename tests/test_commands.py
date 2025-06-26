"""Tests for CLI commands."""

from pathlib import Path
from unittest.mock import Mock

from typer.testing import CliRunner

from sprout.cli import app

runner = CliRunner()


class TestCreateCommand:
    """Test sprout create command."""

    def test_create_success_new_branch(self, mocker, tmp_path):
        """Test successful creation with new branch."""
        # Set up test directory structure
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        sprout_dir = project_dir / ".sprout"
        sprout_dir.mkdir()
        env_example = project_dir / ".env.example"
        env_example.write_text("TEST=value")

        # Create the worktree directory that would be created by git command
        worktree_dir = sprout_dir / "feature-branch"
        worktree_dir.mkdir()

        # Mock prerequisites
        mocker.patch("sprout.commands.create.is_git_repository", return_value=True)
        mocker.patch("sprout.commands.create.get_git_root", return_value=project_dir)
        mocker.patch("sprout.commands.create.worktree_exists", return_value=False)
        mocker.patch("sprout.commands.create.branch_exists", return_value=False)
        mocker.patch("sprout.commands.create.ensure_sprout_dir", return_value=sprout_dir)
        mocker.patch("sprout.commands.create.parse_env_template", return_value="ENV_VAR=value")
        mocker.patch("pathlib.Path.cwd", return_value=project_dir)

        # Mock command execution
        mock_run = mocker.patch("sprout.commands.create.run_command")

        # Run command
        result = runner.invoke(app, ["create", "feature-branch"])

        assert result.exit_code == 0
        assert "✅ Workspace 'feature-branch' created successfully!" in result.stdout
        assert mock_run.called

        # Verify .env file was created
        env_file = sprout_dir / "feature-branch" / ".env"
        assert env_file.exists()
        assert env_file.read_text() == "ENV_VAR=value"

    def test_create_not_in_git_repo(self, mocker):
        """Test error when not in git repository."""
        mocker.patch("sprout.commands.create.is_git_repository", return_value=False)

        result = runner.invoke(app, ["create", "feature-branch"])

        assert result.exit_code == 1
        assert "Not in a git repository" in result.stdout

    def test_create_no_env_example(self, mocker):
        """Test error when .env.example doesn't exist."""
        mocker.patch("sprout.commands.create.is_git_repository", return_value=True)
        mocker.patch("sprout.commands.create.get_git_root", return_value=Path("/project"))

        mock_env_example = Mock()
        mock_env_example.exists.return_value = False
        mocker.patch("pathlib.Path.__truediv__", return_value=mock_env_example)

        result = runner.invoke(app, ["create", "feature-branch"])

        assert result.exit_code == 1
        assert ".env.example file not found" in result.stdout

    def test_create_worktree_exists(self, mocker):
        """Test error when worktree already exists."""
        mocker.patch("sprout.commands.create.is_git_repository", return_value=True)
        mocker.patch("sprout.commands.create.get_git_root", return_value=Path("/project"))
        mocker.patch("sprout.commands.create.worktree_exists", return_value=True)

        mock_env_example = Mock()
        mock_env_example.exists.return_value = True
        mocker.patch("pathlib.Path.__truediv__", return_value=mock_env_example)

        result = runner.invoke(app, ["create", "feature-branch"])

        assert result.exit_code == 1
        assert "Worktree for branch 'feature-branch' already exists" in result.stdout


class TestLsCommand:
    """Test sprout ls command."""

    def test_ls_with_worktrees(self, mocker, tmp_path):
        """Test listing worktrees."""
        # Set up test directory structure
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        sprout_dir = project_dir / ".sprout"
        sprout_dir.mkdir()

        # Create worktree directories
        feature1_dir = sprout_dir / "feature1"
        feature1_dir.mkdir()
        feature2_dir = sprout_dir / "feature2"
        feature2_dir.mkdir()

        # Mock prerequisites
        mocker.patch("sprout.commands.ls.is_git_repository", return_value=True)
        mocker.patch("sprout.commands.ls.get_sprout_dir", return_value=sprout_dir)
        mocker.patch("pathlib.Path.cwd", return_value=project_dir)

        # Mock git worktree list output
        mock_result = Mock()
        mock_result.stdout = f"""worktree {feature1_dir}
HEAD abc123
branch refs/heads/feature1

worktree {feature2_dir}
HEAD def456
branch refs/heads/feature2
"""
        mocker.patch("sprout.commands.ls.run_command", return_value=mock_result)

        result = runner.invoke(app, ["ls"])

        assert result.exit_code == 0
        assert "Sprout Worktrees" in result.stdout
        assert "feature1" in result.stdout
        assert "feature2" in result.stdout

    def test_ls_no_worktrees(self, mocker):
        """Test listing when no worktrees exist."""
        mocker.patch("sprout.commands.ls.is_git_repository", return_value=True)
        mocker.patch("sprout.commands.ls.get_sprout_dir", return_value=Path("/project/.sprout"))

        mock_result = Mock()
        mock_result.stdout = ""
        mocker.patch("sprout.commands.ls.run_command", return_value=mock_result)

        result = runner.invoke(app, ["ls"])

        assert result.exit_code == 0
        assert "No sprout-managed worktrees found" in result.stdout

    def test_ls_not_in_git_repo(self, mocker):
        """Test error when not in git repository."""
        mocker.patch("sprout.commands.ls.is_git_repository", return_value=False)

        result = runner.invoke(app, ["ls"])

        assert result.exit_code == 1
        assert "Not in a git repository" in result.stdout


class TestRmCommand:
    """Test sprout rm command."""

    def test_rm_success_confirm_all(self, mocker):
        """Test successful removal with branch deletion."""
        mocker.patch("sprout.commands.rm.is_git_repository", return_value=True)
        mocker.patch("sprout.commands.rm.worktree_exists", return_value=True)
        mocker.patch("sprout.commands.rm.get_sprout_dir", return_value=Path("/project/.sprout"))

        # Mock user confirmations
        mocker.patch("rich.prompt.Confirm.ask", side_effect=[True, True])

        # Mock command execution
        mock_run = mocker.patch("sprout.commands.rm.run_command")
        mock_run.return_value = Mock(returncode=0)

        result = runner.invoke(app, ["rm", "feature-branch"])

        assert result.exit_code == 0
        assert "✅ Worktree removed successfully" in result.stdout
        assert "✅ Branch deleted successfully" in result.stdout

    def test_rm_cancel_worktree_removal(self, mocker):
        """Test cancelling worktree removal."""
        mocker.patch("sprout.commands.rm.is_git_repository", return_value=True)
        mocker.patch("sprout.commands.rm.worktree_exists", return_value=True)
        mocker.patch("sprout.commands.rm.get_sprout_dir", return_value=Path("/project/.sprout"))

        # User cancels first prompt
        mocker.patch("rich.prompt.Confirm.ask", return_value=False)

        result = runner.invoke(app, ["rm", "feature-branch"])

        assert result.exit_code == 0
        assert "Cancelled" in result.stdout

    def test_rm_worktree_not_exists(self, mocker):
        """Test error when worktree doesn't exist."""
        mocker.patch("sprout.commands.rm.is_git_repository", return_value=True)
        mocker.patch("sprout.commands.rm.worktree_exists", return_value=False)

        result = runner.invoke(app, ["rm", "feature-branch"])

        assert result.exit_code == 1
        assert "Worktree for branch 'feature-branch' does not exist" in result.stdout


class TestPathCommand:
    """Test sprout path command."""

    def test_path_success(self, mocker):
        """Test getting worktree path."""
        mocker.patch("sprout.commands.path.is_git_repository", return_value=True)
        mocker.patch("sprout.commands.path.worktree_exists", return_value=True)
        mocker.patch("sprout.commands.path.get_sprout_dir", return_value=Path("/project/.sprout"))

        result = runner.invoke(app, ["path", "feature-branch"])

        assert result.exit_code == 0
        assert result.stdout.strip() == "/project/.sprout/feature-branch"

    def test_path_worktree_not_exists(self, mocker):
        """Test error when worktree doesn't exist."""
        mocker.patch("sprout.commands.path.is_git_repository", return_value=True)
        mocker.patch("sprout.commands.path.worktree_exists", return_value=False)

        result = runner.invoke(app, ["path", "feature-branch"])

        assert result.exit_code == 1
        # Error goes to stderr, not stdout in path command
        assert "Error: Worktree for branch 'feature-branch' does not exist" in result.output


class TestVersion:
    """Test version display."""

    def test_version_flag(self):
        """Test --version flag."""
        result = runner.invoke(app, ["--version"])

        assert result.exit_code == 0
        assert "sprout version" in result.stdout
