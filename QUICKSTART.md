# Quick Start Guide

Fast reference for common timelog workflows. See [SETUP.md](SETUP.md) for full command reference.

---

## Daily Workflow

### Morning: See your tasks
```bash
timelog tasks
```
Output:
```
Your assigned tasks:

   1. WRSHALLOWFORD-27986 [Ready]           HRFS0 Authoring - Strategy
   2. WRSHALLOWFORD-26964 [In Review]       brelse - Authoring TC
   3. WRSHALLOWFORD-26718 [In Review]       sysClkRateSet - Authoring TC
   ...
```

### Start working on a task
```bash
# Method 1: Use task number from list
timelog start 1 "Started the morning work"

# Method 2: Use ticket key directly
timelog start WRSHALLOWFORD-27986 "Started the morning work"
```

### Check how long you've been working
```bash
timelog status
```
Output:
```
Running:  WRSHALLOWFORD-27986 -- Started the morning work
Started:  09:15:32
Elapsed:  1h 23m
```

### Finish working on task (post to JIRA)
```bash
timelog done
```
Output:
```
Stopping timer for WRSHALLOWFORD-27986 -- 1h 23m to be logged
Posting worklog to JIRA... done! (worklog #12345)

   Ticket:      WRSHALLOWFORD-27986
   Description: Started the morning work
   Time logged: 1h 23m
   Worklog URL: https://jira.critical.pt/browse/WRSHALLOWFORD-27986
```

---

## Common Scenarios

### Scenario 1: Switch to a different task
```bash
# You're working on PROJ-1, now need to switch to PROJ-2
timelog start PROJ-2 "New task" --replace
```
This automatically:
1. Posts the PROJ-1 worklog to JIRA
2. Starts a new timer for PROJ-2

### Scenario 2: Work that started earlier
```bash
# Started work at 2:30 PM, it's now 4:00 PM
timelog start PROJ-123 "Afternoon work" --started 14:30

# Or: started 2 hours ago
timelog start PROJ-123 "Morning work" --started "2h ago"
```

### Scenario 3: Update ticket status while starting
```bash
timelog start PROJ-123 "Working on this" --status "In Progress"
```
This:
1. Starts the timer
2. Updates the JIRA ticket status to "In Progress"

### Scenario 4: Filter tasks by project
```bash
# See only WRSHALLOWFORD tasks
timelog tasks --project WRSHALLOWFORD

# Then start by number
timelog start 1 "Working on it"
```

### Scenario 5: Cancel work (don't post)
```bash
timelog start PROJ-123 "Oops, started by mistake"
# ... work a bit ...
timelog cancel
# Timer is discarded, nothing posted to JIRA
```

---

## End of Day Reports

### View today's worklogs
```bash
timelog today
```
Shows all work logged today with durations and descriptions.

### View this week's worklogs
```bash
timelog week
```
Shows all work logged Monday through today.

---

## Configuration

### View your current config
```bash
timelog config
```
Shows your JIRA host, email, and token (masked for security).

### Change your settings
```bash
# Change JIRA host
timelog config host https://jira.critical.pt

# Change email
timelog config email john.doe

# Update token
timelog config token <new-token>
```

---

## Troubleshooting Quick Fixes

| Problem | Solution |
|---------|----------|
| "Timer already running" | Use `timelog done` to stop, or `timelog start ... --replace` to switch |
| "No timer running" | Use `timelog start <TICKET> "<desc>"` to start a timer |
| "JIRA API error 401" | Check your token: `timelog config token <new-token>` |
| "Ticket not found" | Check your task list: `timelog tasks` |
| "Can't switch tasks" | Use `--replace` flag: `timelog start PROJ-2 "work" --replace` |

---

## Time Format Examples

All these work:

```bash
# Specific time today (24-hour format)
timelog start PROJ-123 "work" --started 14:30
timelog start PROJ-123 "work" --started 09:00

# Time ago (hours)
timelog start PROJ-123 "work" --started "1h ago"
timelog start PROJ-123 "work" --started "2.5h ago"

# Time ago (minutes)
timelog start PROJ-123 "work" --started "30m ago"
timelog start PROJ-123 "work" --started "45m ago"

# Mix hours and minutes
timelog start PROJ-123 "work" --started "1h 30m ago"
```

---

## Full Command Reference

Quick lookup:

```bash
timelog tasks [--project <PROJ>]              # List tasks
timelog start <TICKET> "<desc>" [OPTIONS]    # Start timer
timelog status                                # Show running timer
timelog done                                  # Stop & post to JIRA
timelog cancel                                # Stop without posting
timelog today                                 # View today's work
timelog week                                  # View week's work
timelog config                                # View settings
timelog config <key> <value>                  # Change setting
```

For more details, see [SETUP.md](SETUP.md).

---

## Getting Started Now

1. **First time setup:** See [INSTALL.md](INSTALL.md)
2. **List your tasks:** `timelog tasks`
3. **Start your first timer:** `timelog start 1 "My first task"`
4. **Check progress:** `timelog status`
5. **End of work:** `timelog done`

That's it! You're time tracking. 🎉

---

## Pro Tips

💡 **Tip 1:** Use `--replace` to quickly switch between tasks without manual posting.

💡 **Tip 2:** Use `--started` to log work done earlier (mistakes happen!).

💡 **Tip 3:** Use `timelog today` before leaving to verify all work was logged.

💡 **Tip 4:** Filter by project to focus: `timelog tasks --project WRSHALLOWFORD`

💡 **Tip 5:** Start with status update: `timelog start PROJ-1 "work" --status "In Progress"`

---

## Questions?

- **Setup issues?** See [INSTALL.md](INSTALL.md)
- **Full reference?** See [SETUP.md](SETUP.md)
- **Version history?** See [CHANGELOG.md](CHANGELOG.md)
- **Features?** See [README.md](README.md)
