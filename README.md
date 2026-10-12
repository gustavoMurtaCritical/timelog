# timelog — JIRA Worklog CLI

A lightweight command-line tool to log work time to JIRA directly from your terminal.

## What It Does

**timelog** lets you track work time on JIRA tickets and post worklogs without leaving the command line:

```bash
timelog start PROJ-123 "Building the API endpoint"
# ... do work ...
timelog status
# Running:  PROJ-123 -- Building the API endpoint
# Elapsed:  45m 32s
timelog done
# Stopping timer for PROJ-123 -- 45m 32s to be logged
# Posting worklog to JIRA... done! (worklog #12345)
```

View your daily or weekly worklogs:
```bash
timelog today
timelog week
```

## Features

- **Fast timer** — Start/stop work logging in seconds
- **No dependencies** — Pure Python, works on Windows/Mac/Linux
- **Secure** — Token stored locally, never sent anywhere but JIRA
- **Smart formatting** — Duration as "1h 23m", times in your local zone
- **History** — View today's or this week's worklogs in formatted tables
- **Simple config** — One-time setup of JIRA host, email, and token

## Quick Start

**1. Install:**
- Python 3.8+ required
- Copy this folder to your machine
- Add folder to your PATH (see [SETUP.md](SETUP.md) for details)

**2. Configure:**
```bash
timelog config host https://jira.your-domain.com
timelog config email your-username
timelog config token <your-personal-access-token>
```

**3. Use:**
```bash
timelog start TICKET-1 "Your task description"
timelog done
```

See [SETUP.md](SETUP.md) for full installation instructions, troubleshooting, and all available commands.

## Commands

| Command | Purpose |
|---------|---------|
| `timelog tasks [--project <PROJ>]` | List your assigned tasks (optionally filtered by project) |
| `timelog start <TICKET> "<desc>"` | Start timer for a ticket |
| `timelog start <TICKET> "<desc>" --started "14:30"` | Start timer at specific time today |
| `timelog start <TICKET> "<desc>" --started "1.5h ago"` | Start timer 1.5 hours ago |
| `timelog start <TICKET> "<desc>" --replace` | Auto-replace running timer |
| `timelog start <TICKET> "<desc>" --status "In Progress"` | Start and update ticket status |
| `timelog status` | Show running timer and elapsed time |
| `timelog done` | Stop and post worklog to JIRA |
| `timelog cancel` | Discard timer without posting |
| `timelog today` | Show all worklogs posted today |
| `timelog week` | Show worklogs posted this week (Mon–today) |
| `timelog config` | View your JIRA configuration |

## Features in Detail

### Task Selection
```bash
timelog tasks                          # List all your tasks
timelog tasks --project WRSHALLOWFORD  # Filter by project
timelog start 1 "Working on this"      # Start using task number
```

### Custom Start Times
Log work that started in the past:
```bash
timelog start PROJ-123 "Morning work" --started 09:00      # Start at 9 AM today
timelog start PROJ-123 "Work from earlier" --started "2h ago"  # Started 2 hours ago
```

### Auto-Replace Timer
Switch tasks without manual posting:
```bash
# Currently working on PROJ-123, need to switch to PROJ-456
timelog start PROJ-456 "New task" --replace
# Automatically posts PROJ-123 worklog and starts PROJ-456 timer
```

### Status Updates
```bash
timelog start PROJ-123 "Task" --status "In Progress"
# Starts timer AND updates ticket status in JIRA
```

## How It Works

1. `timelog start` saves the ticket, description, and start time to `~/.timelog_state.json`
2. `timelog status` reads that file and shows elapsed time
3. `timelog done` calculates duration and posts via JIRA REST API v2, then clears the state file
4. `timelog cancel` just clears the state without posting
5. `timelog tasks` fetches your assigned tasks and caches them locally

Your JIRA credentials are stored in `~/.timelog.cfg` (one-time setup).

## Requirements

- **Windows 10+, macOS 10.14+, or Linux**
- **Python 3.8 or later** ([download](https://python.org/downloads))
- **JIRA access** with Personal Access Token authentication

## Getting Help

**[→ See SETUP.md for full installation & troubleshooting](SETUP.md)**

Not working? Common issues:
- `timelog` not recognized → Restart terminal after adding to PATH
- JIRA API error 401 → Check username and token in `timelog config`
- JIRA API error 404 → Verify ticket ID and JIRA host URL

## License

Developed for Critical Software.

---

**Ready to get started?** [→ Go to SETUP.md](SETUP.md)
