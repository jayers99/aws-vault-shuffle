#!/usr/bin/env python3
"""Unit tests for CLI module."""

import pytest

from aws_vault_shuffle import __version__
from aws_vault_shuffle.cli import create_parser, main


class TestCLIVersion:
    """Tests for version flag."""

    def test_version_flag(self, capsys):
        """Test --version flag displays correct version."""
        parser = create_parser()

        with pytest.raises(SystemExit) as exc_info:
            parser.parse_args(["--version"])

        assert exc_info.value.code == 0
        captured = capsys.readouterr()
        assert __version__ in captured.out


class TestCLIListCommand:
    """Tests for 'list' command."""

    def test_list_with_account_and_regions(self):
        """Test list command with account and regions."""
        parser = create_parser()
        args = parser.parse_args([
            "list",
            "--account", "123456789012",
            "--regions", "us-east-1,us-west-2",
        ])

        assert args.command == "list"
        assert args.account == "123456789012"
        assert args.regions == "us-east-1,us-west-2"
        assert args.output == "table"  # default

    def test_list_with_config_file(self):
        """Test list command with config file."""
        parser = create_parser()
        args = parser.parse_args([
            "list",
            "--config", "config.yml",
        ])

        assert args.command == "list"
        assert args.config == "config.yml"

    def test_list_with_output_format(self):
        """Test list command with custom output format."""
        parser = create_parser()
        args = parser.parse_args([
            "list",
            "--account", "123456789012",
            "--regions", "us-east-1",
            "--output", "json",
        ])

        assert args.output == "json"

    def test_dry_run_flag(self):
        """Test --dry-run flag is parsed (must come before subcommand)."""
        parser = create_parser()
        args = parser.parse_args([
            "--dry-run",
            "list",
            "--account", "123456789012",
            "--regions", "us-east-1",
        ])

        assert args.dry_run is True


class TestCLIMain:
    """Tests for main() function."""

    def test_main_no_command_shows_help(self, capsys):
        """Test running with no command shows help."""
        exit_code = main([])
        assert exit_code == 1

        captured = capsys.readouterr()
        assert "usage:" in captured.out.lower()

    def test_main_list_requires_account_without_config(self, capsys):
        """Test list command requires --account when not using --config."""
        exit_code = main(["list", "--regions", "us-east-1"])
        assert exit_code == 1

        captured = capsys.readouterr()
        assert "account is required" in captured.err.lower()

    def test_main_list_requires_regions_without_config(self, capsys):
        """Test list command requires --regions when not using --config."""
        exit_code = main(["list", "--account", "123456789012"])
        assert exit_code == 1

        captured = capsys.readouterr()
        assert "regions is required" in captured.err.lower()

    def test_main_list_with_valid_args(self, capsys):
        """Test list command with valid arguments."""
        exit_code = main([
            "list",
            "--account", "123456789012",
            "--regions", "us-east-1,us-west-2",
        ])

        # Currently returns 0 with placeholder message
        assert exit_code == 0

        captured = capsys.readouterr()
        assert "123456789012" in captured.out
        assert "us-east-1,us-west-2" in captured.out
