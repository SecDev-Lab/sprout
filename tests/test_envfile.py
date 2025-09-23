"""Tests for the envfile command."""

from unittest.mock import MagicMock, patch

from sprout.commands.envfile import create_env_files, find_env_example_files, get_current_branch
from sprout.exceptions import SproutError


class TestGetCurrentBranch:
    """Test get_current_branch function."""

    def test_get_current_branch_success(self):
        """Test successful branch retrieval."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="feature-branch\n")
            assert get_current_branch() == "feature-branch"

    def test_get_current_branch_head_state(self):
        """Test when in detached HEAD state."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="HEAD\n")
            assert get_current_branch() is None

    def test_get_current_branch_failure(self):
        """Test when git command fails."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=1)
            assert get_current_branch() is None

    def test_get_current_branch_no_git(self):
        """Test when git is not available."""
        with patch("subprocess.run", side_effect=FileNotFoundError):
            assert get_current_branch() is None


class TestFindEnvExampleFiles:
    """Test find_env_example_files function."""

    def test_find_env_example_files(self, tmp_path):
        """Test finding .env.example files recursively."""
        # Create test structure
        (tmp_path / "dir1").mkdir()
        (tmp_path / "dir1" / ".env.example").touch()
        (tmp_path / "dir2").mkdir()
        (tmp_path / "dir2" / "subdir").mkdir()
        (tmp_path / "dir2" / "subdir" / ".env.example").touch()
        (tmp_path / ".env").touch()  # Should not be found

        files = find_env_example_files(tmp_path)
        assert len(files) == 2
        assert all(f.name == ".env.example" for f in files)

    def test_find_env_example_files_empty(self, tmp_path):
        """Test when no .env.example files exist."""
        files = find_env_example_files(tmp_path)
        assert files == []

    def test_find_env_example_files_sorted(self, tmp_path):
        """Test that files are returned sorted."""
        (tmp_path / "b").mkdir()
        (tmp_path / "b" / ".env.example").touch()
        (tmp_path / "a").mkdir()
        (tmp_path / "a" / ".env.example").touch()

        files = find_env_example_files(tmp_path)
        assert len(files) == 2
        assert files[0].parent.name == "a"
        assert files[1].parent.name == "b"


class TestCreateEnvFiles:
    """Test create_env_files function."""

    @patch("sprout.commands.envfile.Path.cwd")
    @patch("sprout.commands.envfile.get_current_branch")
    @patch("sprout.commands.envfile.get_used_ports")
    @patch("sprout.commands.envfile.parse_env_template")
    def test_create_env_files_basic(self, mock_parse, mock_ports, mock_branch, mock_cwd, tmp_path):
        """Test basic .env file creation."""
        # Setup
        mock_cwd.return_value = tmp_path
        mock_branch.return_value = "main"
        mock_ports.return_value = set()
        mock_parse.return_value = "KEY=value\n"

        # Create .env.example
        (tmp_path / ".env.example").write_text("KEY={{ VALUE }}\n")

        # Run
        with patch("sprout.commands.envfile.console"):
            create_env_files()

        # Verify
        assert (tmp_path / ".env").exists()
        assert (tmp_path / ".env").read_text() == "KEY=value\n"

    @patch("sprout.commands.envfile.Path.cwd")
    def test_create_env_files_skip_existing(self, mock_cwd, tmp_path):
        """Test skipping existing .env files."""
        mock_cwd.return_value = tmp_path

        # Create existing .env and .env.example
        (tmp_path / ".env").write_text("existing")
        (tmp_path / ".env.example").write_text("new")

        with patch("sprout.commands.envfile.console"):
            create_env_files(force=False)

        # Should not overwrite
        assert (tmp_path / ".env").read_text() == "existing"

    @patch("sprout.commands.envfile.Path.cwd")
    @patch("sprout.commands.envfile.get_current_branch")
    @patch("sprout.commands.envfile.get_used_ports")
    @patch("sprout.commands.envfile.parse_env_template")
    def test_create_env_files_force(self, mock_parse, mock_ports, mock_branch, mock_cwd, tmp_path):
        """Test forcing overwrite of existing .env files."""
        mock_cwd.return_value = tmp_path
        mock_branch.return_value = "main"
        mock_ports.return_value = set()
        mock_parse.return_value = "new"

        # Create existing .env and .env.example
        (tmp_path / ".env").write_text("existing")
        (tmp_path / ".env.example").write_text("template")

        with patch("sprout.commands.envfile.console"):
            create_env_files(force=True)

        # Should overwrite
        assert (tmp_path / ".env").read_text() == "new"

    @patch("sprout.commands.envfile.Path.cwd")
    @patch("sprout.commands.envfile.get_current_branch")
    @patch("sprout.commands.envfile.get_used_ports")
    def test_create_env_files_dry_run(self, mock_ports, mock_branch, mock_cwd, tmp_path):
        """Test dry run mode."""
        mock_cwd.return_value = tmp_path
        mock_branch.return_value = "main"
        mock_ports.return_value = set()

        # Create .env.example
        (tmp_path / ".env.example").write_text("KEY=value\n")

        with patch("sprout.commands.envfile.console"):
            create_env_files(dry_run=True)

        # Should not create .env
        assert not (tmp_path / ".env").exists()

    @patch("sprout.commands.envfile.Path.cwd")
    def test_create_env_files_no_examples(self, mock_cwd, tmp_path):
        """Test when no .env.example files exist."""
        mock_cwd.return_value = tmp_path

        with patch("sprout.commands.envfile.console") as mock_console:
            create_env_files()
            # Should print warning
            mock_console.print.assert_called()

    @patch("sprout.commands.envfile.Path.cwd")
    @patch("sprout.commands.envfile.get_current_branch")
    @patch("sprout.commands.envfile.get_used_ports")
    @patch("sprout.commands.envfile.parse_env_template")
    def test_create_env_files_recursive(
        self, mock_parse, mock_ports, mock_branch, mock_cwd, tmp_path
    ):
        """Test recursive .env file creation."""
        mock_cwd.return_value = tmp_path
        mock_branch.return_value = "main"
        mock_ports.return_value = set()
        mock_parse.return_value = "KEY=value\n"

        # Create nested structure
        (tmp_path / "app1").mkdir()
        (tmp_path / "app1" / ".env.example").write_text("APP1={{ VALUE }}\n")
        (tmp_path / "app2").mkdir()
        (tmp_path / "app2" / ".env.example").write_text("APP2={{ VALUE }}\n")

        with patch("sprout.commands.envfile.console"):
            create_env_files()

        # Verify both .env files created
        assert (tmp_path / "app1" / ".env").exists()
        assert (tmp_path / "app2" / ".env").exists()

    @patch("sprout.commands.envfile.Path.cwd")
    @patch("sprout.commands.envfile.get_current_branch")
    @patch("sprout.commands.envfile.get_used_ports")
    @patch("sprout.commands.envfile.parse_env_template")
    def test_create_env_files_error_handling(
        self, mock_parse, mock_ports, mock_branch, mock_cwd, tmp_path
    ):
        """Test error handling during file creation."""
        mock_cwd.return_value = tmp_path
        mock_branch.return_value = "main"
        mock_ports.return_value = set()
        mock_parse.side_effect = SproutError("Template error")

        # Create .env.example
        (tmp_path / ".env.example").write_text("KEY={{ VALUE }}\n")

        with patch("sprout.commands.envfile.console"):
            create_env_files()

        # Should not create .env due to error
        assert not (tmp_path / ".env").exists()

    @patch("sprout.commands.envfile.Path.cwd")
    def test_create_env_files_silent_mode(self, mock_cwd, tmp_path):
        """Test silent mode suppresses output."""
        mock_cwd.return_value = tmp_path

        with patch("sprout.commands.envfile.console") as mock_console:
            create_env_files(silent=True)
            # Should not print anything in silent mode
            mock_console.print.assert_not_called()
