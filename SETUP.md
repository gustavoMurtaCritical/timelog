# timelog — Setup Guide

## Requirements

- Windows 10 or later
- Python 3.8 or later — download from https://python.org/downloads
  - During install: check **"Add Python to PATH"** and **"Install for all users"**

---

## Steps

### 1. Copy the folder

Place the folder containing `timelog.py` and `timelog.bat` anywhere on the machine,
for example: `C:\Users\<you>\scripts\timelog\`

### 2. Add the folder to your PATH

Open PowerShell and run (replace the path with wherever you placed the folder):

```powershell
setx PATH "%PATH%;C:\Users\<you>\scripts\timelog"
```

Close and reopen the terminal after running this.

### 3. Set your credentials

To get a Personal Access Token:
- Log into https://jira.critical.pt
- Click your profile picture > Profile > Personal Access Tokens > Create token
- Copy the token

Then run these three commands in your terminal:

```
timelog config host https://jira.critical.pt
timelog config email your-jira-username
timelog config token your-personal-access-token
```

This creates `C:\Users\<you>\.timelog.cfg` automatically. To verify what was saved:

```
timelog config
```

The token will be masked in the output for security.

### 4. Verify it works

Open a new terminal and run:

```
timelog
```

You should see the usage message. Then do a live test with a real ticket:

```
timelog start PROJ-123 "Testing setup"
timelog status
timelog done
```

Check the Work log tab on that JIRA ticket to confirm the entry posted.

---

## Usage

| Command | Description |
|---|---|
| `timelog tasks` | Show all your assigned tasks |
| `timelog tasks --project <PROJ>` | Show tasks for a specific project |
| `timelog start <TICKET-ID> "<description>"` | Start a timer for a ticket |
| `timelog start <TICKET> "<desc>" --started "14:30"` | Start at specific time today |
| `timelog start <TICKET> "<desc>" --started "1.5h ago"` | Start N hours/minutes ago |
| `timelog start <TICKET> "<desc>" --status "<status>"` | Start and update ticket status |
| `timelog start <TICKET> "<desc>" --replace` | Replace running timer (auto-posts) |
| `timelog status` | Show the running timer and elapsed time |
| `timelog done` | Stop the timer and post the worklog to JIRA |
| `timelog cancel` | Discard the timer without posting anything |
| `timelog today` | Show all worklogs posted today |
| `timelog week` | Show all worklogs posted this week |
| `timelog config` | Show all config values (token is masked) |
| `timelog config <key>` | Show a single value (`host`, `email`, or `token`) |
| `timelog config <key> <value>` | Set a config value |

---

## Troubleshooting

| Error | Fix |
|---|---|
| `timelog` not recognized | PATH not set, or terminal not restarted after `setx` |
| `python` not recognized | Python not installed or not added to PATH during install |
| Config file not found | Create `~\.timelog.cfg` as described in step 3 |
| JIRA API error 401 | Wrong username or token in `.timelog.cfg` |
| JIRA API error 403 | Token lacks permissions, or expired — generate a new one |
| JIRA API error 404 | Ticket ID doesn't exist, or `host` is wrong in `.timelog.cfg` |
