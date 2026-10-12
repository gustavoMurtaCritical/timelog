#!/usr/bin/env python3
"""
Unit tests for timelog.py

Run with: python -m unittest test_timelog
Or:       python -m pytest test_timelog.py (if pytest is installed)
"""

import unittest
import tempfile
import shutil
import json
import configparser
from pathlib import Path
from datetime import datetime, timezone, timedelta
from unittest.mock import patch, MagicMock
import sys

# Import the functions we want to test
# We need to adjust paths since test will run from repo root
sys.path.insert(0, str(Path(__file__).parent))
import timelog


class TestDurationFormatting(unittest.TestCase):
    """Test the _format_duration function."""

    def test_format_seconds_only(self):
        """Test formatting seconds under 60."""
        self.assertEqual(timelog._format_duration(30), "30s")
        self.assertEqual(timelog._format_duration(59), "59s")

    def test_format_minutes_and_seconds(self):
        """Test formatting minutes and seconds."""
        self.assertEqual(timelog._format_duration(90), "1m 30s")
        self.assertEqual(timelog._format_duration(125), "2m 05s")

    def test_format_hours_and_minutes(self):
        """Test formatting hours (seconds are omitted when hours present)."""
        self.assertEqual(timelog._format_duration(3600), "1h 00m")
        self.assertEqual(timelog._format_duration(5400), "1h 30m")
        self.assertEqual(timelog._format_duration(7325), "2h 02m")

    def test_format_large_values(self):
        """Test formatting large time values."""
        self.assertEqual(timelog._format_duration(36000), "10h 00m")  # 10 hours
        self.assertEqual(timelog._format_duration(86400), "24h 00m")  # 24 hours


class TestConfigManagement(unittest.TestCase):
    """Test config file operations."""

    def setUp(self):
        """Create a temporary directory for config files."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = Path(self.temp_dir) / ".timelog.cfg"
        self.state_file = Path(self.temp_dir) / ".timelog_state.json"

        # Patch the config and state file paths
        self.patcher_config = patch.object(timelog, 'CONFIG_FILE', self.config_file)
        self.patcher_state = patch.object(timelog, 'STATE_FILE', self.state_file)
        self.patcher_config.start()
        self.patcher_state.start()

    def tearDown(self):
        """Clean up temporary directory and patches."""
        self.patcher_config.stop()
        self.patcher_state.stop()
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_config_file_missing(self):
        """Test that missing config file triggers appropriate error."""
        with self.assertRaises(SystemExit):
            timelog._load_config()

    def test_save_and_load_config(self):
        """Test saving and loading configuration."""
        cfg = configparser.ConfigParser()
        cfg["jira"] = {
            "host": "https://jira.example.com",
            "email": "user@example.com",
            "token": "secret-token-123"
        }
        with open(self.config_file, "w", encoding="utf-8") as f:
            cfg.write(f)

        # Load and verify
        host, email, token = timelog._load_config()
        self.assertEqual(host, "https://jira.example.com")
        self.assertEqual(email, "user@example.com")
        self.assertEqual(token, "secret-token-123")

    def test_config_strips_whitespace(self):
        """Test that config values are stripped of whitespace."""
        cfg = configparser.ConfigParser()
        cfg["jira"] = {
            "host": "  https://jira.example.com/  ",
            "email": "  user@example.com  ",
            "token": "  token123  "
        }
        with open(self.config_file, "w", encoding="utf-8") as f:
            cfg.write(f)

        host, email, token = timelog._load_config()
        self.assertEqual(host, "https://jira.example.com")
        self.assertEqual(email, "user@example.com")
        self.assertEqual(token, "token123")

    def test_config_removes_trailing_slash(self):
        """Test that trailing slash is removed from host."""
        cfg = configparser.ConfigParser()
        cfg["jira"] = {
            "host": "https://jira.example.com/",
            "email": "user@example.com",
            "token": "token123"
        }
        with open(self.config_file, "w", encoding="utf-8") as f:
            cfg.write(f)

        host, email, token = timelog._load_config()
        self.assertEqual(host, "https://jira.example.com")


class TestStateManagement(unittest.TestCase):
    """Test state file operations."""

    def setUp(self):
        """Create a temporary directory for state files."""
        self.temp_dir = tempfile.mkdtemp()
        self.state_file = Path(self.temp_dir) / ".timelog_state.json"

        # Patch the state file path
        self.patcher_state = patch.object(timelog, 'STATE_FILE', self.state_file)
        self.patcher_state.start()

    def tearDown(self):
        """Clean up temporary directory and patches."""
        self.patcher_state.stop()
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_load_state_empty(self):
        """Test loading state when no file exists."""
        state = timelog._load_state()
        self.assertEqual(state, {})

    def test_save_and_load_state(self):
        """Test saving and loading state."""
        test_state = {
            "ticket": "PROJ-123",
            "description": "Testing feature",
            "started": datetime.now(timezone.utc).isoformat()
        }
        timelog._save_state(test_state)

        loaded = timelog._load_state()
        self.assertEqual(loaded["ticket"], "PROJ-123")
        self.assertEqual(loaded["description"], "Testing feature")
        self.assertIn("started", loaded)

    def test_clear_state(self):
        """Test clearing state."""
        test_state = {"ticket": "PROJ-123"}
        timelog._save_state(test_state)
        self.assertTrue(self.state_file.exists())

        timelog._clear_state()
        self.assertFalse(self.state_file.exists())

    def test_load_state_after_clear(self):
        """Test that loading after clear returns empty dict."""
        timelog._save_state({"ticket": "PROJ-123"})
        timelog._clear_state()
        state = timelog._load_state()
        self.assertEqual(state, {})


class TestElapsedTime(unittest.TestCase):
    """Test elapsed time calculation."""

    def test_elapsed_time_calculation(self):
        """Test that elapsed time is calculated correctly."""
        # Create a start time 1 hour ago
        start_iso = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()

        elapsed = timelog._elapsed_seconds(start_iso)

        # Should be approximately 3600 seconds (1 hour), allow some tolerance
        self.assertGreater(elapsed, 3595)
        self.assertLess(elapsed, 3605)

    def test_elapsed_time_minimum(self):
        """Test that elapsed time has a minimum of 60 seconds."""
        # Use a start time just now
        start_iso = datetime.now(timezone.utc).isoformat()

        elapsed = timelog._elapsed_seconds(start_iso)

        # Should be at least 60 seconds
        self.assertGreaterEqual(elapsed, 60)


class TestStartCommand(unittest.TestCase):
    """Test the start command."""

    def setUp(self):
        """Create a temporary directory for state files."""
        self.temp_dir = tempfile.mkdtemp()
        self.state_file = Path(self.temp_dir) / ".timelog_state.json"
        self.patcher_state = patch.object(timelog, 'STATE_FILE', self.state_file)
        self.patcher_state.start()

    def tearDown(self):
        """Clean up."""
        self.patcher_state.stop()
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_start_creates_state(self):
        """Test that start command creates state file."""
        with patch('builtins.print'):  # Suppress output
            timelog.cmd_start("PROJ-123", "Test task")

        self.assertTrue(self.state_file.exists())
        state = timelog._load_state()
        self.assertEqual(state["ticket"], "PROJ-123")
        self.assertEqual(state["description"], "Test task")

    def test_start_when_already_running(self):
        """Test that start fails if timer already running."""
        # Start first timer
        with patch('builtins.print'):
            timelog.cmd_start("PROJ-123", "First task")

        # Try to start another
        with self.assertRaises(SystemExit):
            timelog.cmd_start("PROJ-456", "Second task")


class TestCancelCommand(unittest.TestCase):
    """Test the cancel command."""

    def setUp(self):
        """Create a temporary directory for state files."""
        self.temp_dir = tempfile.mkdtemp()
        self.state_file = Path(self.temp_dir) / ".timelog_state.json"
        self.patcher_state = patch.object(timelog, 'STATE_FILE', self.state_file)
        self.patcher_state.start()

    def tearDown(self):
        """Clean up."""
        self.patcher_state.stop()
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_cancel_clears_state(self):
        """Test that cancel clears the state file."""
        # Start a timer
        with patch('builtins.print'):
            timelog.cmd_start("PROJ-123", "Test task")

        self.assertTrue(self.state_file.exists())

        # Cancel it
        with patch('builtins.print'):
            timelog.cmd_cancel()

        self.assertFalse(self.state_file.exists())

    def test_cancel_when_no_timer(self):
        """Test that cancel handles no running timer gracefully."""
        with patch('builtins.print'):
            timelog.cmd_cancel()  # Should not raise

        self.assertFalse(self.state_file.exists())


class TestStatusCommand(unittest.TestCase):
    """Test the status command."""

    def setUp(self):
        """Create a temporary directory for state files."""
        self.temp_dir = tempfile.mkdtemp()
        self.state_file = Path(self.temp_dir) / ".timelog_state.json"
        self.patcher_state = patch.object(timelog, 'STATE_FILE', self.state_file)
        self.patcher_state.start()

    def tearDown(self):
        """Clean up."""
        self.patcher_state.stop()
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_status_no_timer(self):
        """Test status when no timer is running."""
        with patch('builtins.print') as mock_print:
            timelog.cmd_status()
            mock_print.assert_called_with("No timer running.")

    def test_status_shows_running_timer(self):
        """Test status shows info about running timer."""
        with patch('builtins.print'):
            timelog.cmd_start("PROJ-123", "Test task")

        with patch('builtins.print') as mock_print:
            timelog.cmd_status()

            # Verify print was called multiple times with the expected info
            calls = mock_print.call_args_list
            output = " ".join(str(call) for call in calls)

            self.assertIn("PROJ-123", output)
            self.assertIn("Test task", output)


# ─────────────────────────────────────────────────────────────────────────────
# Integration tests (require network/JIRA access)
# ─────────────────────────────────────────────────────────────────────────────

class TestTaskManagement(unittest.TestCase):
    """Test task listing and selection."""

    def setUp(self):
        """Create temporary files."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = Path(self.temp_dir) / ".timelog.cfg"
        self.state_file = Path(self.temp_dir) / ".timelog_state.json"
        self.tasks_cache_file = Path(self.temp_dir) / ".timelog_tasks_cache.json"

        self.patcher_config = patch.object(timelog, 'CONFIG_FILE', self.config_file)
        self.patcher_state = patch.object(timelog, 'STATE_FILE', self.state_file)
        self.patcher_cache = patch.object(timelog, 'TASKS_CACHE_FILE', self.tasks_cache_file)
        self.patcher_config.start()
        self.patcher_state.start()
        self.patcher_cache.start()

    def tearDown(self):
        """Clean up."""
        self.patcher_config.stop()
        self.patcher_state.stop()
        self.patcher_cache.stop()
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch('timelog._jira_get')
    def test_fetch_assigned_tasks(self, mock_jira_get):
        """Test fetching assigned tasks from JIRA."""
        # Setup config first
        cfg = configparser.ConfigParser()
        cfg["jira"] = {
            "host": "https://jira.example.com",
            "email": "user@example.com",
            "token": "token123"
        }
        with open(self.config_file, "w", encoding="utf-8") as f:
            cfg.write(f)

        mock_jira_get.return_value = {
            "issues": [
                {
                    "key": "PROJ-123",
                    "fields": {
                        "summary": "Build API",
                        "status": {"name": "Open"}
                    }
                },
                {
                    "key": "PROJ-456",
                    "fields": {
                        "summary": "Fix bug",
                        "status": {"name": "In Progress"}
                    }
                }
            ]
        }

        tasks = timelog._fetch_assigned_tasks()

        self.assertEqual(len(tasks), 2)
        self.assertEqual(tasks[0]["ticket"], "PROJ-123")
        self.assertEqual(tasks[0]["status"], "Open")
        self.assertEqual(tasks[1]["ticket"], "PROJ-456")
        self.assertEqual(tasks[1]["status"], "In Progress")

    def test_start_with_task_index(self):
        """Test starting timer using task index."""
        # Setup cache with tasks
        tasks = [
            {"ticket": "PROJ-123", "summary": "Build API", "status": "Open"},
            {"ticket": "PROJ-456", "summary": "Fix bug", "status": "In Progress"}
        ]
        self.tasks_cache_file.write_text(json.dumps(tasks), encoding="utf-8")

        with patch('builtins.print'):
            timelog.cmd_start("1", "Working on it")

        state = timelog._load_state()
        self.assertEqual(state["ticket"], "PROJ-123")
        self.assertEqual(state["description"], "Working on it")

    def test_start_with_invalid_index(self):
        """Test starting timer with invalid task index."""
        tasks = [
            {"ticket": "PROJ-123", "summary": "Build API", "status": "Open"}
        ]
        self.tasks_cache_file.write_text(json.dumps(tasks), encoding="utf-8")

        with self.assertRaises(SystemExit):
            timelog.cmd_start("99", "Working on it")

    def test_start_with_direct_ticket(self):
        """Test starting timer with direct ticket key."""
        with patch('builtins.print'):
            timelog.cmd_start("PROJ-123", "Working on it")

        state = timelog._load_state()
        self.assertEqual(state["ticket"], "PROJ-123")


class TestTimeManagement(unittest.TestCase):
    """Test custom start time and auto-replace features."""

    def setUp(self):
        """Create temporary files."""
        self.temp_dir = tempfile.mkdtemp()
        self.state_file = Path(self.temp_dir) / ".timelog_state.json"
        self.tasks_cache_file = Path(self.temp_dir) / ".timelog_tasks_cache.json"

        self.patcher_state = patch.object(timelog, 'STATE_FILE', self.state_file)
        self.patcher_cache = patch.object(timelog, 'TASKS_CACHE_FILE', self.tasks_cache_file)
        self.patcher_state.start()
        self.patcher_cache.start()

    def tearDown(self):
        """Clean up."""
        self.patcher_state.stop()
        self.patcher_cache.stop()
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_parse_start_time_hhmm_format(self):
        """Test parsing HH:MM format."""
        result = timelog._parse_start_time("14:30")
        self.assertIsInstance(result, datetime)
        # Convert to local time to check hour and minute
        local_result = result.astimezone()
        self.assertEqual(local_result.hour, 14)
        self.assertEqual(local_result.minute, 30)

    def test_parse_start_time_hours_ago(self):
        """Test parsing 'N hours ago' format."""
        now = datetime.now(timezone.utc)
        result = timelog._parse_start_time("2h ago")

        # Should be approximately 2 hours ago
        diff = (now - result).total_seconds()
        self.assertGreater(diff, 7100)  # > 1h 58m
        self.assertLess(diff, 7300)     # < 2h 2m

    def test_parse_start_time_minutes_ago(self):
        """Test parsing 'N minutes ago' format."""
        now = datetime.now(timezone.utc)
        result = timelog._parse_start_time("45m ago")

        # Should be approximately 45 minutes ago
        diff = (now - result).total_seconds()
        self.assertGreater(diff, 2600)  # > 43m
        self.assertLess(diff, 2800)     # < 47m

    def test_parse_start_time_decimal_hours(self):
        """Test parsing decimal hours (e.g., 1.5h ago)."""
        now = datetime.now(timezone.utc)
        result = timelog._parse_start_time("1.5h ago")

        # Should be approximately 1.5 hours ago
        diff = (now - result).total_seconds()
        self.assertGreater(diff, 5300)  # > 1h 28m
        self.assertLess(diff, 5500)     # < 1h 32m

    def test_start_with_custom_time(self):
        """Test starting timer with custom start time."""
        with patch('builtins.print'):
            timelog.cmd_start("PROJ-123", "Task", start_time_str="1h ago")

        state = timelog._load_state()
        self.assertEqual(state["ticket"], "PROJ-123")

        # Verify start time is approximately 1 hour ago
        start = datetime.fromisoformat(state["started"])
        now = datetime.now(timezone.utc)
        diff = (now - start).total_seconds()
        self.assertGreater(diff, 3500)  # > 58m
        self.assertLess(diff, 3700)     # < 62m

    def test_auto_replace_timer(self):
        """Test auto-replacing running timer."""
        # Start first timer
        with patch('builtins.print'):
            timelog.cmd_start("PROJ-123", "First task")

        state = timelog._load_state()
        self.assertEqual(state["ticket"], "PROJ-123")

        # Mock cmd_done to avoid JIRA calls
        with patch.object(timelog, 'cmd_done'):
            with patch('builtins.print'):
                timelog.cmd_start("PROJ-456", "Second task", replace=True)

        # Should have new timer
        state = timelog._load_state()
        self.assertEqual(state["ticket"], "PROJ-456")

    def test_start_without_replace_fails(self):
        """Test that starting without replace fails if timer running."""
        # Start first timer
        with patch('builtins.print'):
            timelog.cmd_start("PROJ-123", "First task")

        # Try to start without replace should fail
        with self.assertRaises(SystemExit):
            timelog.cmd_start("PROJ-456", "Second task", replace=False)


class TestIntegration(unittest.TestCase):
    """Integration tests requiring JIRA connectivity."""

    def setUp(self):
        """Create temporary files."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = Path(self.temp_dir) / ".timelog.cfg"
        self.state_file = Path(self.temp_dir) / ".timelog_state.json"

        self.patcher_config = patch.object(timelog, 'CONFIG_FILE', self.config_file)
        self.patcher_state = patch.object(timelog, 'STATE_FILE', self.state_file)
        self.patcher_config.start()
        self.patcher_state.start()

    def tearDown(self):
        """Clean up."""
        self.patcher_config.stop()
        self.patcher_state.stop()
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch('urllib.request.urlopen')
    def test_post_worklog_success(self, mock_urlopen):
        """Test successful worklog posting (mocked)."""
        # Setup config
        cfg = configparser.ConfigParser()
        cfg["jira"] = {
            "host": "https://jira.example.com",
            "email": "user@example.com",
            "token": "token123"
        }
        with open(self.config_file, "w", encoding="utf-8") as f:
            cfg.write(f)

        # Mock JIRA response
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({"id": "12345"}).encode("utf-8")
        mock_urlopen.return_value.__enter__.return_value = mock_response

        # Test posting
        start_time = datetime.now(timezone.utc).isoformat()
        result, host = timelog._post_worklog("PROJ-123", start_time, 3600, "Test work")

        self.assertEqual(result["id"], "12345")
        self.assertEqual(host, "https://jira.example.com")

    @patch('urllib.request.urlopen')
    def test_update_issue_status(self, mock_urlopen):
        """Test updating issue status (mocked)."""
        # Setup config
        cfg = configparser.ConfigParser()
        cfg["jira"] = {
            "host": "https://jira.example.com",
            "email": "user@example.com",
            "token": "token123"
        }
        with open(self.config_file, "w", encoding="utf-8") as f:
            cfg.write(f)

        # Mock JIRA responses
        mock_response = MagicMock()
        # First call is to get transitions
        mock_response.read.side_effect = [
            json.dumps({
                "transitions": [
                    {"id": "11", "to": {"name": "Open"}},
                    {"id": "21", "to": {"name": "In Progress"}},
                    {"id": "31", "to": {"name": "Done"}}
                ]
            }).encode("utf-8"),
            b""  # Second call is transition POST, returns empty
        ]
        mock_urlopen.return_value.__enter__.return_value = mock_response

        # Test status update (should not raise)
        timelog._update_issue_status("PROJ-123", "In Progress")


# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    unittest.main(verbosity=2)
