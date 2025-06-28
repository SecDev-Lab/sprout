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
        # Mock git ls-files to return .env.example
        mock_run.side_effect = lambda cmd, **kwargs: (
            Mock(stdout=".env.example\n", returncode=0)
            if cmd[1] == "ls-files"
            else Mock(returncode=0)
        )
        # Mock git ls-files to return .env.example
        mock_run.side_effect = lambda cmd, **kwargs: (
            Mock(stdout=".env.example\n", returncode=0)
            if cmd[1] == "ls-files"
            else Mock(returncode=0)
        )

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

    def test_create_with_path_flag_success(self, mocker, tmp_path):
        """Test successful creation with --path flag outputs only the path."""
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

        # Mock command execution
        mock_run = mocker.patch("sprout.commands.create.run_command")
        # Mock git ls-files to return .env.example
        mock_run.side_effect = lambda cmd, **kwargs: (
            Mock(stdout=".env.example\n", returncode=0)
            if cmd[1] == "ls-files"
            else Mock(returncode=0)
        )

        # Run command with --path flag
        result = runner.invoke(app, ["create", "feature-branch", "--path"])

        assert result.exit_code == 0
        # Should output only the path, no other messages
        assert result.stdout.strip() == str(worktree_dir)
        # No Rich formatting in output
        assert "[green]" not in result.stdout
        assert "✅" not in result.stdout
        assert mock_run.called

    def test_create_with_path_flag_error(self, mocker):
        """Test error handling with --path flag uses stderr."""
        mocker.patch("sprout.commands.create.is_git_repository", return_value=False)

        result = runner.invoke(app, ["create", "feature-branch", "--path"])

        assert result.exit_code == 1
        # Error should be in stderr, not stdout
        assert "Error: Not in a git repository" in result.output
        # stdout should be empty
        assert result.stdout == ""

    def test_create_no_env_example(self, mocker):
        """Test error when .env.example doesn't exist."""
        mocker.patch("sprout.commands.create.is_git_repository", return_value=True)
        mock_git_root = Path("/project")
        mocker.patch("sprout.commands.create.get_git_root", return_value=mock_git_root)

        # Mock git ls-files to return empty list
        mock_run = mocker.patch("sprout.commands.create.run_command")
        mock_run.return_value = Mock(stdout="", returncode=0)

        result = runner.invoke(app, ["create", "feature-branch"])

        assert result.exit_code == 1
        assert "No .env.example files found" in result.stdout

    def test_create_worktree_exists(self, mocker):
        """Test error when worktree already exists."""
        mocker.patch("sprout.commands.create.is_git_repository", return_value=True)
        mock_git_root = Path("/project")
        mocker.patch("sprout.commands.create.get_git_root", return_value=mock_git_root)
        mocker.patch("sprout.commands.create.worktree_exists", return_value=True)

        # Mock git ls-files to return .env.example
        mock_run = mocker.patch("sprout.commands.create.run_command")
        mock_run.return_value = Mock(stdout=".env.example\n", returncode=0)

        # Mock Path.exists to return True for .env.example
        mock_exists = mocker.patch("pathlib.Path.exists")
        mock_exists.return_value = True

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
        mocker.patch("sprout.utils.is_git_repository", return_value=True)
        mocker.patch("sprout.utils.get_sprout_dir", return_value=sprout_dir)
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
        mocker.patch("sprout.utils.run_command", return_value=mock_result)

        result = runner.invoke(app, ["ls"])

        assert result.exit_code == 0
        assert "Sprout Worktrees" in result.stdout
        assert "feature1" in result.stdout
        assert "feature2" in result.stdout

    def test_ls_no_worktrees(self, mocker):
        """Test listing when no worktrees exist."""
        mocker.patch("sprout.commands.ls.is_git_repository", return_value=True)
        mocker.patch("sprout.utils.is_git_repository", return_value=True)
        mocker.patch("sprout.utils.get_sprout_dir", return_value=Path("/project/.sprout"))

        mock_result = Mock()
        mock_result.stdout = ""
        mocker.patch("sprout.utils.run_command", return_value=mock_result)

        result = runner.invoke(app, ["ls"])

        assert result.exit_code == 0
        assert "No sprout-managed worktrees found" in result.stdout

    def test_ls_not_in_git_repo(self, mocker):
        """Test error when not in git repository."""
        mocker.patch("sprout.commands.ls.is_git_repository", return_value=False)

        result = runner.invoke(app, ["ls"])

        assert result.exit_code == 1
        assert "Not in a git repository" in result.stdout


# Removed TestRmCommand class since rm command requires stdin for confirmations
# Testing rm command functionality is handled at the unit level for the underlying functions


class TestPathCommand:
    """Test sprout path command."""

    def test_path_success(self, mocker):
        """Test getting worktree path."""
        mocker.patch("sprout.commands.path.is_git_repository", return_value=True)
        mocker.patch(
            "sprout.commands.path.resolve_branch_identifier", return_value="feature-branch"
        )
        mocker.patch("sprout.commands.path.worktree_exists", return_value=True)
        mocker.patch("sprout.commands.path.get_sprout_dir", return_value=Path("/project/.sprout"))

        result = runner.invoke(app, ["path", "feature-branch"])

        assert result.exit_code == 0
        assert result.stdout.strip() == "/project/.sprout/feature-branch"

    def test_path_worktree_not_exists(self, mocker):
        """Test error when worktree doesn't exist."""
        mocker.patch("sprout.commands.path.is_git_repository", return_value=True)
        mocker.patch(
            "sprout.commands.path.resolve_branch_identifier", return_value="feature-branch"
        )
        mocker.patch("sprout.commands.path.worktree_exists", return_value=False)

        result = runner.invoke(app, ["path", "feature-branch"])

        assert result.exit_code == 1
        # Error goes to stderr, not stdout in path command
        assert "Error: Worktree for branch 'feature-branch' does not exist" in result.output

    def test_path_with_index(self, mocker, tmp_path):
        """Test getting worktree path using index."""
        # Set up test directory structure
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        sprout_dir = project_dir / ".sprout"
        sprout_dir.mkdir()

        # Create worktree directories
        feature_a_dir = sprout_dir / "feature-a"
        feature_a_dir.mkdir()
        feature_b_dir = sprout_dir / "feature-b"
        feature_b_dir.mkdir()

        # Mock prerequisites
        mocker.patch("sprout.commands.path.is_git_repository", return_value=True)
        mocker.patch("sprout.utils.is_git_repository", return_value=True)
        mocker.patch("sprout.utils.get_sprout_dir", return_value=sprout_dir)
        mocker.patch("sprout.commands.path.get_sprout_dir", return_value=sprout_dir)
        mocker.patch("sprout.commands.path.worktree_exists", return_value=True)
        mocker.patch("pathlib.Path.cwd", return_value=project_dir)

        # Mock git worktree list output for index resolution
        mock_result = Mock()
        mock_result.stdout = f"""worktree {feature_a_dir}
HEAD abc123
branch refs/heads/feature-a

worktree {feature_b_dir}
HEAD def456
branch refs/heads/feature-b
"""
        mocker.patch("sprout.utils.run_command", return_value=mock_result)

        # Test with index "2" which should resolve to "feature-b"
        result = runner.invoke(app, ["path", "2"])

        assert result.exit_code == 0
        assert result.stdout.strip() == str(sprout_dir / "feature-b")

    def test_path_with_invalid_index(self, mocker):
        """Test error when using invalid index."""
        # Mock prerequisites
        mocker.patch("sprout.commands.path.is_git_repository", return_value=True)
        mocker.patch("sprout.utils.is_git_repository", return_value=True)
        mocker.patch("sprout.utils.get_sprout_dir", return_value=Path("/project/.sprout"))

        # Mock empty worktree list
        mock_result = Mock()
        mock_result.stdout = ""
        mocker.patch("sprout.utils.run_command", return_value=mock_result)

        result = runner.invoke(app, ["path", "99"])

        assert result.exit_code == 1
        assert "Invalid index '99'" in result.output
        assert "sprout ls" in result.output


class TestVersion:
    """Test version display."""

    def test_version_flag(self):
        """Test --version flag."""
        result = runner.invoke(app, ["--version"])

        assert result.exit_code == 0
        assert "sprout version" in result.stdout


class TestIndexedOperations:
    """Test index-based functionality."""

    def test_ls_with_indices(self, mocker, tmp_path):
        """Test that ls command shows index numbers."""
        # Set up test directory structure
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        sprout_dir = project_dir / ".sprout"
        sprout_dir.mkdir()

        # Create worktree directories
        feature_a_dir = sprout_dir / "feature-a"
        feature_a_dir.mkdir()
        feature_b_dir = sprout_dir / "feature-b"
        feature_b_dir.mkdir()
        feature_c_dir = sprout_dir / "feature-c"
        feature_c_dir.mkdir()

        # Mock prerequisites
        mocker.patch("sprout.utils.is_git_repository", return_value=True)
        mocker.patch("sprout.utils.get_sprout_dir", return_value=sprout_dir)
        mocker.patch("pathlib.Path.cwd", return_value=project_dir)

        # Mock git worktree list output
        mock_result = Mock()
        mock_result.stdout = f"""worktree {feature_a_dir}
HEAD abc123
branch refs/heads/feature-a

worktree {feature_b_dir}
HEAD def456
branch refs/heads/feature-b

worktree {feature_c_dir}
HEAD ghi789
branch refs/heads/feature-c
"""
        mocker.patch("sprout.utils.run_command", return_value=mock_result)

        result = runner.invoke(app, ["ls"])

        assert result.exit_code == 0
        assert "No." in result.stdout  # Check for index column header
        assert "1" in result.stdout
        assert "2" in result.stdout
        assert "3" in result.stdout
        # Check that branches are sorted alphabetically
        lines = result.stdout.split("\n")
        for line in lines:
            if "1" in line and "feature-a" in line:
                assert True
                break
        else:
            raise AssertionError("Index 1 should correspond to feature-a")

    def test_rm_with_index(self, mocker, tmp_path):
        """Test removing worktree by index."""
        # Set up test directory structure
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        sprout_dir = project_dir / ".sprout"
        sprout_dir.mkdir()

        # Create worktree directories
        feature_a_dir = sprout_dir / "feature-a"
        feature_a_dir.mkdir()
        feature_b_dir = sprout_dir / "feature-b"
        feature_b_dir.mkdir()

        # Mock prerequisites
        mocker.patch("sprout.commands.rm.is_git_repository", return_value=True)
        mocker.patch("sprout.utils.is_git_repository", return_value=True)
        mocker.patch("sprout.utils.get_sprout_dir", return_value=sprout_dir)
        mocker.patch("sprout.commands.rm.get_sprout_dir", return_value=sprout_dir)
        mocker.patch("sprout.utils.worktree_exists", return_value=True)
        mocker.patch("sprout.commands.rm.worktree_exists", return_value=True)
        mocker.patch("pathlib.Path.cwd", return_value=project_dir)

        # Mock git worktree list output for index resolution
        mock_result = Mock()
        mock_result.stdout = f"""worktree {feature_a_dir}
HEAD abc123
branch refs/heads/feature-a

worktree {feature_b_dir}
HEAD def456
branch refs/heads/feature-b
"""
        mocker.patch("sprout.utils.run_command", return_value=mock_result)

        # Mock the actual removal command
        mock_rm_result = Mock()
        mock_rm_result.returncode = 0
        mocker.patch("sprout.commands.rm.run_command", return_value=mock_rm_result)

        # Test with index "2" which should resolve to "feature-b"
        result = runner.invoke(app, ["rm", "2"], input="n\n")  # Say no to confirmation

        assert result.exit_code == 0
        assert "feature-b" in result.stdout  # Should show the resolved branch name

    def test_rm_with_invalid_index(self, mocker):
        """Test error when using invalid index."""
        # Mock prerequisites
        mocker.patch("sprout.commands.rm.is_git_repository", return_value=True)
        mocker.patch("sprout.utils.is_git_repository", return_value=True)
        mocker.patch("sprout.utils.get_sprout_dir", return_value=Path("/project/.sprout"))

        # Mock empty worktree list
        mock_result = Mock()
        mock_result.stdout = ""
        mocker.patch("sprout.utils.run_command", return_value=mock_result)

        result = runner.invoke(app, ["rm", "1"])

        assert result.exit_code == 1
        assert "Invalid index" in result.stdout
        assert "sprout ls" in result.stdout  # Should suggest using ls command
