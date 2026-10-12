# Changelog

All notable changes to timelog are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.2.0] — 2026-10-01

### Added

- **Custom start times for timers**
  - `--started HH:MM` — Start timer at specific time today
  - `--started "Nh ago"` — Start timer N hours/minutes ago
  - Examples: `timelog start PROJ-123 "task" --started 14:30` or `--started "1.5h ago"`
  - Useful for logging work that started in the past

- **Auto-replace running timer**
  - `--replace` flag to seamlessly switch between tasks
  - Automatically posts current worklog before starting new timer
  - Example: `timelog start PROJ-456 "new task" --replace`
  - No need for manual `timelog done` before switching

- **Project filtering for task lists**
  - `timelog tasks --project <PROJECT>` to filter by project
  - Example: `timelog tasks --project WRSHALLOWFORD`
  - Reduces clutter when working with many projects

### Improved

- Time parsing with support for flexible input formats
- Smoother task-to-task transitions without manual posting
- Better error messages for invalid time formats

### No Breaking Changes

All v1.1 features remain unchanged. All new flags are optional.

---

## [1.1.0] — 2026-09-11

### Added

- **Comprehensive documentation**
  - New `README.md` with quick-start guide and feature overview
  - Docstrings on all functions for better code maintainability
  - Links to detailed setup and troubleshooting guides

- **Test coverage**
  - Full unit test suite with 21 tests (`test_timelog.py`)
  - Tests cover: config management, state handling, duration formatting, command logic
  - Mocked integration tests for JIRA API calls
  - All tests passing; run with `python -m unittest test_timelog`

- **This CHANGELOG.md**
  - Version history and change tracking for future reference

### Improved

- Code clarity: Added docstrings to all functions explaining purpose, args, and return values
- User experience: README provides immediate context and examples
- Maintainability: Tests ensure regressions are caught early

### No Breaking Changes

All features from v1.0 remain unchanged. This release is backward compatible.

---

## [1.0.0] — 2026-06-26

### Initial Release

**Core Features:**
- Start/stop work timer and log to JIRA
- View daily and weekly worklog summaries
- Configure JIRA credentials securely
- Pure Python, no external dependencies
- Windows/Mac/Linux support

**Commands:**
- `timelog start <TICKET> "<desc>"` — Start timer
- `timelog done` — Stop and post to JIRA
- `timelog status` — Show running timer
- `timelog cancel` — Discard timer
- `timelog today` — Show today's worklogs
- `timelog week` — Show this week's worklogs
- `timelog config` — Manage JIRA configuration

**Documentation:**
- `SETUP.md` — Installation and troubleshooting guide
- `timelog.bat` — Windows command wrapper for convenience

---

## Planned (Future Releases)

### [1.2.0] — Reliability & Debugging (Planned)

- [ ] Verbose logging mode (`--debug` flag)
- [ ] Retry logic with exponential backoff for API failures
- [ ] Better error messages with actionable guidance
- [ ] Timeout handling improvements

### [1.3.0] — Flexibility (Planned)

- [ ] Custom config path (`--config-path` flag)
- [ ] Batch operations (`timelog batch <csv>`)
- [ ] Shell auto-completion support
- [ ] Daily summary exports

---

## How to Report Issues

When reporting a bug, include:
1. Python version (`python --version`)
2. The command that failed
3. Full error message
4. Output of `timelog config` (with token masked)

For security issues, do not use the issue tracker — contact the maintainers directly.

---

## Versioning

This project uses [Semantic Versioning](https://semver.org/):
- **MAJOR** — Breaking changes (incompatible API)
- **MINOR** — New features (backward compatible)
- **PATCH** — Bug fixes (backward compatible)
