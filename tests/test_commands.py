"""Tests for CLI commands."""

from pathlib import Path
from unittest.mock import Mock

from typer.testing import CliRunner

from sprout.cli import app

runner = CliRunner()


class TestCreateCommand:
    """Test sprout create command."""

    def test_create_success_new_branch(self, mocker):
        """Test successful creation with new branch."""
        # Mock prerequisites
        mocker.patch("sprout.commands.create.is_git_repository", return_value=True)
        mocker.patch("sprout.commands.create.get_git_root", return_value=Path("/project"))
        mocker.patch("sprout.commands.create.worktree_exists", return_value=False)
        mocker.patch("sprout.commands.create.branch_exists", return_value=False)
        mocker.patch(
            "sprout.commands.create.ensure_sprout_dir", return_value=Path("/project/.sprout")
        )

        # Mock Path.cwd()
        mocker.patch("pathlib.Path.cwd", return_value=Path("/project"))

        # Mock file operations
        mock_env_file = Mock()
        mocker.patch("sprout.commands.create.parse_env_template", return_value="ENV_VAR=value")

        # Create a more specific mock for worktree_path / ".env"
        mock_worktree_path = Mock()
        mock_worktree_path.__truediv__.return_value = mock_env_file
        mock_worktree_path.relative_to.return_value = Path(".sprout/feature-branch")

        # Mock ensure_sprout_dir to return a mock that creates our mock_worktree_path
        mock_sprout_dir = Mock()
        mock_sprout_dir.__truediv__.return_value = mock_worktree_path
        mocker.patch("sprout.commands.create.ensure_sprout_dir", return_value=mock_sprout_dir)

        # Mock env example
        mock_env_example = Mock()
        mock_env_example.exists.return_value = True
        mock_git_root = Mock()
        mock_git_root.__truediv__.return_value = mock_env_example
        mocker.patch("sprout.commands.create.get_git_root", return_value=mock_git_root)

        # Mock command execution
        mock_run = mocker.patch("sprout.commands.create.run_command")

        # Run command
        result = runner.invoke(app, ["create", "feature-branch"])

        assert result.exit_code == 0
        assert "✅ Workspace 'feature-branch' created successfully!" in result.stdout
        mock_run.assert_called_once()
        mock_env_file.write_text.assert_called_once()

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

    def test_ls_with_worktrees(self, mocker, monkeypatch):
        """Test listing worktrees."""
        mocker.patch("sprout.commands.ls.is_git_repository", return_value=True)

        # Create a proper mock for get_sprout_dir
        mock_sprout_dir = Path("/project/.sprout")
        mocker.patch("sprout.commands.ls.get_sprout_dir", return_value=mock_sprout_dir)

        # Mock git worktree list output
        mock_result = Mock()
        mock_result.stdout = """worktree /project/.sprout/feature1
HEAD abc123
branch refs/heads/feature1

worktree /project/.sprout/feature2
HEAD def456
branch refs/heads/feature2
"""
        mocker.patch("sprout.commands.ls.run_command", return_value=mock_result)

        # Create mock paths with proper attributes
        mock_path1 = Mock(spec=Path)
        mock_path1.resolve.return_value = Path("/project/.sprout/feature1")
        mock_path1.parent = mock_sprout_dir
        mock_path1.exists.return_value = True
        mock_path1.stat.return_value = Mock(st_mtime=1234567890)
        mock_path1.relative_to.return_value = Path(".sprout/feature1")
        mock_path1.__str__.return_value = ".sprout/feature1"

        mock_path2 = Mock(spec=Path)
        mock_path2.resolve.return_value = Path("/project/.sprout/feature2")
        mock_path2.parent = mock_sprout_dir
        mock_path2.exists.return_value = True
        mock_path2.stat.return_value = Mock(st_mtime=1234567890)
        mock_path2.relative_to.return_value = Path(".sprout/feature2")
        mock_path2.__str__.return_value = ".sprout/feature2"

        # Mock Path creation
        def path_side_effect(path_str):
            if path_str == "/project/.sprout/feature1":
                return mock_path1
            elif path_str == "/project/.sprout/feature2":
                return mock_path2
            return Path(path_str)

        mocker.patch("sprout.commands.ls.Path", side_effect=path_side_effect)

        # Mock current path
        mock_cwd = Mock(spec=Path)
        mock_cwd.resolve.return_value = Path("/project")
        mocker.patch("pathlib.Path.cwd", return_value=mock_cwd)

        result = runner.invoke(app, ["ls"])

        assert result.exit_code == 0
        assert "Sprout Worktrees" in result.stdout

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
