#!/usr/bin/env python3
"""
timelog.py -- JIRA worklog CLI
Usage:
  timelog start <TICKET-ID> "<description>"
  timelog done
  timelog status
  timelog cancel
"""

import sys
import json
import configparser
import urllib.request
import urllib.error
import urllib.parse
from datetime import datetime, timezone, date, timedelta
from pathlib import Path

CONFIG_FILE = Path.home() / ".timelog.cfg"
STATE_FILE  = Path.home() / ".timelog_state.json"
TASKS_CACHE_FILE = Path.home() / ".timelog_tasks_cache.json"


def _load_config():
    """
    Load JIRA configuration from ~/.timelog.cfg.

    Returns:
        tuple: (host, email, token) — JIRA host URL, username, and personal access token.

    Raises:
        SystemExit: If config file is missing or required keys are not set.
    """
    if not CONFIG_FILE.exists():
        sys.exit(
            f"ERROR: Config file not found: {CONFIG_FILE}\n\n"
            "Create it with the following content:\n\n"
            "[jira]\n"
            "host  = https://your-domain.atlassian.net\n"
            "email = your-username\n"
            "token = your-personal-access-token\n"
        )
    cfg = configparser.ConfigParser()
    cfg.read(CONFIG_FILE, encoding="utf-8")
    try:
        host  = cfg["jira"]["host"].strip().rstrip("/")
        email = cfg["jira"]["email"].strip()
        token = cfg["jira"]["token"].strip()
    except KeyError as e:
        sys.exit(f"ERROR: Missing key {e} in {CONFIG_FILE} under [jira] section.")
    if not host or not email or not token:
        sys.exit(f"ERROR: host, email, and token must all be set in {CONFIG_FILE}.")
    return host, email, token


def _load_state():
    """
    Load timer state from ~/.timelog_state.json.

    Returns:
        dict: State dict with keys 'ticket', 'description', 'started' if running,
              or empty dict {} if no timer is active.
    """
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    return {}


def _save_state(state):
    """
    Save timer state to ~/.timelog_state.json.

    Args:
        state (dict): State dict with keys 'ticket', 'description', 'started'.
    """
    STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")


def _clear_state():
    """Delete the timer state file."""
    if STATE_FILE.exists():
        STATE_FILE.unlink()


def _parse_start_time(time_str):
    """
    Parse a custom start time string.

    Supports:
      - HH:MM format (assumes today): "14:30"
      - Time ago format: "1.5h ago", "2h 30m ago", "45m ago"

    Args:
        time_str (str): Time string to parse.

    Returns:
        datetime: Parsed datetime in UTC timezone.

    Raises:
        SystemExit: If time string is invalid.
    """
    import re

    # Try HH:MM format (today)
    if re.match(r'^\d{1,2}:\d{2}$', time_str):
        try:
            parts = time_str.split(':')
            hour = int(parts[0])
            minute = int(parts[1])
            # Create datetime for today at specified time
            now = datetime.now(timezone.utc)
            local_now = now.astimezone()
            target = local_now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            # Convert back to UTC
            return target.astimezone(timezone.utc)
        except (ValueError, IndexError):
            sys.exit(f"ERROR: Invalid time format '{time_str}'. Use HH:MM (e.g., 14:30)")

    # Try "time ago" format
    match = re.match(r'^([\d.]+)\s*(h|m|hour|hours|minute|minutes|min|mins)\s+ago$', time_str, re.IGNORECASE)
    if match:
        amount = float(match.group(1))
        unit = match.group(2).lower()

        # Convert to minutes
        if unit in ('h', 'hour', 'hours'):
            minutes_ago = int(amount * 60)
        elif unit in ('m', 'min', 'mins', 'minute', 'minutes'):
            minutes_ago = int(amount)
        else:
            sys.exit(f"ERROR: Unknown time unit '{unit}'")

        # Calculate start time
        start_time = datetime.now(timezone.utc) - timedelta(minutes=minutes_ago)
        return start_time

    sys.exit(
        f"ERROR: Invalid --started format '{time_str}'.\n"
        f"Use HH:MM (e.g., 14:30) or time ago (e.g., '1.5h ago', '45m ago')"
    )


def _elapsed_seconds(start_iso):
    """
    Calculate elapsed seconds since start time.

    Args:
        start_iso (str): ISO 8601 formatted datetime string.

    Returns:
        int: Elapsed seconds (minimum 60).
    """
    start = datetime.fromisoformat(start_iso)
    now   = datetime.now(timezone.utc)
    return max(60, int((now - start).total_seconds()))


def _format_duration(seconds):
    """
    Format seconds into human-readable duration string.

    Args:
        seconds (int): Number of seconds.

    Returns:
        str: Formatted duration (e.g., "1h 23m", "45m 30s", "10s").
    """
    h, rem = divmod(seconds, 3600)
    m, s   = divmod(rem, 60)
    if h:
        return f"{h}h {m:02d}m"
    if m:
        return f"{m}m {s:02d}s"
    return f"{s}s"


def _post_worklog(ticket, started, seconds, comment):
    """
    Post a worklog entry to JIRA via REST API v2.

    Args:
        ticket (str): JIRA ticket key (e.g., "PROJ-123").
        started (str): ISO 8601 formatted start time.
        seconds (int): Duration in seconds.
        comment (str): Worklog comment/description.

    Returns:
        tuple: (result_dict, host) where result_dict contains JIRA response (includes 'id').

    Raises:
        SystemExit: On network error or HTTP error from JIRA API.
    """
    host, email, token = _load_config()

    dt = datetime.fromisoformat(started).astimezone(timezone.utc)
    started_jira = dt.strftime("%Y-%m-%dT%H:%M:%S.000+0000")

    payload = json.dumps({
        "started":          started_jira,
        "timeSpentSeconds": seconds,
        "comment":          comment,
    }).encode("utf-8")

    req = urllib.request.Request(
        f"{host}/rest/api/2/issue/{ticket}/worklog",
        data=payload,
        headers={
            "Authorization":     f"Bearer {token}",
            "Content-Type":      "application/json",
            "Accept":            "application/json",
            "X-Atlassian-Token": "no-check",
            "X-Requested-With":  "XMLHttpRequest",
            "Origin":            host,
            "User-Agent":        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode("utf-8")), host
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        sys.exit(f"JIRA API error {e.code}: {body}")
    except urllib.error.URLError as e:
        sys.exit(f"Network error: {e.reason}")


def _fetch_assigned_tasks(project=None):
    """
    Fetch tasks assigned to the current user, optionally filtered by project.

    Args:
        project (str, optional): JIRA project key to filter by (e.g., "WRSHALLOWFORD").

    Returns:
        list: List of task dicts with keys: ticket, summary, status.

    Raises:
        SystemExit: On JIRA API errors.
    """
    host, email, token = _load_config()

    jql = 'assignee = currentUser()'
    if project:
        jql += f' AND project = {project.upper()}'

    encoded_jql = urllib.parse.quote(jql)
    path = f"/rest/api/2/search?jql={encoded_jql}&fields=summary,status&maxResults=100"
    result = _jira_get(path, host, token)

    tasks = []
    for issue in result.get("issues", []):
        tasks.append({
            "ticket": issue["key"],
            "summary": issue["fields"].get("summary", ""),
            "status": issue["fields"].get("status", {}).get("name", "Unknown"),
        })

    # Cache tasks locally for quick reference
    TASKS_CACHE_FILE.write_text(json.dumps(tasks, indent=2), encoding="utf-8")
    return tasks


def _update_issue_status(ticket, new_status):
    """
    Update the status of a JIRA issue.

    Args:
        ticket (str): JIRA ticket key (e.g., "PROJ-123").
        new_status (str): Target status name (e.g., "In Progress").

    Raises:
        SystemExit: On JIRA API errors.
    """
    host, email, token = _load_config()

    # Get available transitions for this issue
    transitions = _jira_get(
        f"/rest/api/2/issue/{ticket}/transitions",
        host, token,
    )

    # Find the transition ID for the target status
    transition_id = None
    for trans in transitions.get("transitions", []):
        if trans.get("to", {}).get("name", "").lower() == new_status.lower():
            transition_id = trans.get("id")
            break

    if not transition_id:
        available = [t.get("to", {}).get("name") for t in transitions.get("transitions", [])]
        sys.exit(
            f"ERROR: Status '{new_status}' not available for {ticket}.\n"
            f"Available statuses: {', '.join(available)}"
        )

    # Perform the transition
    payload = json.dumps({"transition": {"id": transition_id}}).encode("utf-8")
    req = urllib.request.Request(
        f"{host}/rest/api/2/issue/{ticket}/transitions",
        data=payload,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-Atlassian-Token": "no-check",
            "X-Requested-With": "XMLHttpRequest",
            "Origin": host,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            resp.read()  # consume response
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        sys.exit(f"JIRA API error {e.code}: {body}")
    except urllib.error.URLError as e:
        sys.exit(f"Network error: {e.reason}")


def cmd_start(ticket_or_index, description, status=None, start_time_str=None, replace=False):
    """
    Start a timer for a ticket.

    Args:
        ticket_or_index (str): JIRA ticket key (e.g., "PROJ-123") or task index (e.g., "1").
        description (str): Work description.
        status (str, optional): Update ticket status (e.g., "In Progress").
        start_time_str (str, optional): Custom start time ("14:30" or "1.5h ago").
        replace (bool, optional): If True, replace running timer with new one.

    Raises:
        SystemExit: If a timer is already running (unless replace=True) or ticket is invalid.
    """
    # Check if already running
    state = _load_state()
    if state:
        if not replace:
            running = state.get("ticket", "?")
            elapsed = _format_duration(_elapsed_seconds(state["started"]))
            sys.exit(f"ERROR: Timer already running for {running} ({elapsed} elapsed).\nRun 'timelog done' or 'timelog cancel' first.")
        else:
            # Auto-replace: post the current worklog first
            print(f"Posting worklog for {state.get('ticket', '?')}...", end=" ", flush=True)
            cmd_done()
            print("done!")
            state = None  # Clear state after posting

    # Resolve ticket ID from index or direct key
    ticket = ticket_or_index.upper()
    if ticket.isdigit():
        # Task index — load from cache
        if not TASKS_CACHE_FILE.exists():
            sys.exit(f"ERROR: Task cache not found. Run 'timelog tasks' first to load your task list.")
        try:
            tasks = json.loads(TASKS_CACHE_FILE.read_text(encoding="utf-8"))
            idx = int(ticket) - 1
            if idx < 0 or idx >= len(tasks):
                sys.exit(f"ERROR: Task #{ticket} not found. Run 'timelog tasks' to see your task list.")
            ticket = tasks[idx]["ticket"]
        except (json.JSONDecodeError, ValueError) as e:
            sys.exit(f"ERROR: Invalid task cache. Run 'timelog tasks' again. ({e})")

    # Update status if requested
    if status:
        print(f"Updating {ticket} status to '{status}'...", end=" ", flush=True)
        _update_issue_status(ticket, status)
        print("done!")

    # Determine start time
    if start_time_str:
        start_time = _parse_start_time(start_time_str)
    else:
        start_time = datetime.now(timezone.utc)

    # Save state and start timer
    _save_state({"ticket": ticket, "description": description, "started": start_time.isoformat()})
    print(f"Started timer for {ticket}: {description}")
    start_local = start_time.astimezone().strftime('%H:%M:%S')
    print(f"Started at {start_local}")


def cmd_done():
    """
    Stop the running timer and post worklog to JIRA.

    Raises:
        SystemExit: If no timer is running or if JIRA API call fails.
    """
    state = _load_state()
    if not state:
        sys.exit("ERROR: No timer running. Use 'timelog start <TICKET-ID> \"<description>\"' first.")
    ticket      = state["ticket"]
    description = state["description"]
    started     = state["started"]
    seconds     = _elapsed_seconds(started)
    duration    = _format_duration(seconds)
    print(f"Stopping timer for {ticket} -- {duration} to be logged")
    print(f"Posting worklog to JIRA...", end=" ", flush=True)
    result, host = _post_worklog(ticket, started, seconds, description)
    _clear_state()
    worklog_id = result.get("id", "?")
    print(f"done! (worklog #{worklog_id})")
    print(f"\n   Ticket:      {ticket}")
    print(f"   Description: {description}")
    print(f"   Time logged: {duration}")
    print(f"   Worklog URL: {host}/browse/{ticket}")


def cmd_status():
    """Display the currently running timer and elapsed time."""
    state = _load_state()
    if not state:
        print("No timer running.")
        return
    ticket      = state["ticket"]
    description = state["description"]
    started     = state["started"]
    elapsed     = _elapsed_seconds(started)
    duration    = _format_duration(elapsed)
    start_local = datetime.fromisoformat(started).astimezone().strftime("%H:%M:%S")
    print(f"Running:  {ticket} -- {description}")
    print(f"Started:  {start_local}")
    print(f"Elapsed:  {duration}")


def _jira_get(path, host, token):
    """
    Make an authenticated GET request to JIRA REST API.

    Args:
        path (str): API path (e.g., "/rest/api/2/search?jql=...").
        host (str): JIRA host URL.
        token (str): Personal access token.

    Returns:
        dict: Parsed JSON response from JIRA.

    Raises:
        SystemExit: On network error or HTTP error from JIRA API.
    """
    req = urllib.request.Request(
        f"{host}{path}",
        headers={
            "Authorization":     f"Bearer {token}",
            "Accept":            "application/json",
            "X-Atlassian-Token": "no-check",
            "X-Requested-With":  "XMLHttpRequest",
            "Origin":            host,
            "User-Agent":        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        sys.exit(f"JIRA API error {e.code}: {body}")
    except urllib.error.URLError as e:
        sys.exit(f"Network error: {e.reason}")


def _fetch_worklogs_for_range(start_date, end_date):
    """
    Fetch all worklogs for the current user within a date range.

    Args:
        start_date (date): Start date (inclusive).
        end_date (date): End date (inclusive).

    Returns:
        list: List of worklog dicts, each with keys:
            - ticket (str): JIRA ticket key
            - summary (str): Ticket summary/title
            - comment (str): Worklog description
            - seconds (int): Time logged in seconds
            - logged_date (date): Date the worklog was logged

    Raises:
        SystemExit: On JIRA API errors.
    """
    host, email, token = _load_config()

    # Step 1: find tickets that have worklogs by currentUser in the range
    jql = (
        f'worklogAuthor = currentUser() '
        f'AND worklogDate >= "{start_date}" '
        f'AND worklogDate <= "{end_date}"'
    )
    encoded_jql = urllib.parse.quote(jql)
    search = _jira_get(
        f"/rest/api/2/search?jql={encoded_jql}&fields=summary&maxResults=100",
        host, token,
    )

    issues = search.get("issues", [])
    if not issues:
        return []

    results = []

    # Step 2: for each ticket, fetch its worklogs and keep only ours in range
    for issue in issues:
        ticket  = issue["key"]
        summary = issue["fields"].get("summary", "")
        wl_data = _jira_get(
            f"/rest/api/2/issue/{ticket}/worklog?maxResults=100",
            host, token,
        )
        for wl in wl_data.get("worklogs", []):
            author = wl.get("author", {})
            # match by username (name) or display name containing our email prefix
            author_name = author.get("name", "").lower()
            if author_name != email.lower():
                continue
            # started is "2024-06-25T09:00:00.000+0000"
            started_str = wl.get("started", "")
            try:
                logged_date = datetime.strptime(started_str[:10], "%Y-%m-%d").date()
            except ValueError:
                continue
            if not (start_date <= logged_date <= end_date):
                continue
            results.append({
                "ticket":      ticket,
                "summary":     summary,
                "comment":     wl.get("comment", ""),
                "seconds":     wl.get("timeSpentSeconds", 0),
                "logged_date": logged_date,
            })

    results.sort(key=lambda x: x["logged_date"])
    return results


def _print_worklog_report(entries, label):
    """
    Print worklogs in a formatted table grouped by day.

    Args:
        entries (list): List of worklog dicts from _fetch_worklogs_for_range.
        label (str): Display label for the report (e.g., "today (11 Sep 2026)").
    """
    # Column widths
    TW = 22   # ticket
    DW = 8    # duration
    CW = 34   # comment
    # Full inner width: TW + DW + CW + 6 (for " | " x2 and padding)
    IW = TW + DW + CW + 6  # = 70

    top    = "+" + "-" * (IW + 2) + "+"
    div    = "+" + "-" * (TW + 2) + "+" + "-" * (DW + 2) + "+" + "-" * (CW + 2) + "+"
    bottom = "+" + "-" * (IW + 2) + "+"

    def full_row(text, fill=" "):
        return "| " + text.ljust(IW) + " |"

    def data_row(ticket, duration, comment):
        t = ticket[:TW].ljust(TW)
        d = duration[:DW].ljust(DW)
        c = comment[:CW].ljust(CW)
        return f"| {t} | {d} | {c} |"

    if not entries:
        print(f"\nNo worklogs found for {label}.")
        return

    total_seconds = sum(e["seconds"] for e in entries)
    print(f"\nWorklogs for {label}\n")

    # Group by day
    days = {}
    for e in entries:
        days.setdefault(e["logged_date"], []).append(e)

    for day, day_entries in days.items():
        day_seconds = sum(e["seconds"] for e in day_entries)
        day_label   = day.strftime("%A, %d %b %Y")

        print(top)
        print(full_row(f"  {day_label}"))
        print(div)
        for e in day_entries:
            comment  = e["comment"][:CW] + "..." if len(e["comment"]) > CW else e["comment"]
            duration = _format_duration(e["seconds"])
            print(data_row(e["ticket"], duration, comment))
        print(div)
        print(full_row(f"  Day total: {_format_duration(day_seconds)}"))
        print(bottom)
        print()

    print(f"  Total: {_format_duration(total_seconds)}\n")


def cmd_today():
    """Display all worklogs posted today."""
    today = date.today()
    entries = _fetch_worklogs_for_range(today, today)
    _print_worklog_report(entries, f"today ({today.strftime('%d %b %Y')})")


def cmd_week():
    """Display all worklogs posted this week (Monday to today)."""
    today  = date.today()
    monday = today - timedelta(days=today.weekday())  # weekday() 0=Mon
    entries = _fetch_worklogs_for_range(monday, today)
    label = f"this week ({monday.strftime('%d %b')} – {today.strftime('%d %b %Y')})"
    _print_worklog_report(entries, label)


def cmd_tasks(project=None):
    """
    Display tasks assigned to the current user, optionally filtered by project.

    Args:
        project (str, optional): JIRA project key to filter by.

    Shows task ID, key, status, and summary in a formatted list.
    """
    filter_text = f" in {project.upper()}" if project else ""
    print(f"Fetching assigned tasks{filter_text} from JIRA...", end=" ", flush=True)
    tasks = _fetch_assigned_tasks(project=project)
    print("done!\n")

    if not tasks:
        print("No tasks assigned to you.")
        return

    # Format and display
    print("Your assigned tasks:\n")
    for i, task in enumerate(tasks, 1):
        status_padded = f"[{task['status']}]".ljust(18)
        print(f"  {i:2d}. {task['ticket']:15s} {status_padded} {task['summary'][:50]}")

    print(f"\nTotal: {len(tasks)} task(s)")
    print("\nUsage: timelog start <number-or-ticket> \"<description>\" [--status \"<new-status>\"]")
    print("Example: timelog start 1 \"Working on this\" --status \"In Progress\"")


def cmd_cancel():
    """Discard the running timer without posting to JIRA."""
    state = _load_state()
    if not state:
        print("No timer running -- nothing to cancel.")
        return
    ticket  = state["ticket"]
    elapsed = _format_duration(_elapsed_seconds(state["started"]))
    _clear_state()
    print(f"Cancelled timer for {ticket} ({elapsed} discarded, nothing posted to JIRA).")


def cmd_config(args):
    """
    Manage JIRA configuration (host, email, token).

    Args:
        args (list): Command arguments:
            - [] : Show all config values (token is masked)
            - [key] : Show a single value
            - [key, value] : Set a config value

    Valid keys: host, email, token
    """
    valid_keys = {"host", "email", "token"}

    # ── read current config (or start fresh) ─────────────────────────────────
    cfg = configparser.ConfigParser()
    if CONFIG_FILE.exists():
        cfg.read(CONFIG_FILE, encoding="utf-8")
    if "jira" not in cfg:
        cfg["jira"] = {}

    # timelog config  →  show all
    if not args:
        print(f"Config file: {CONFIG_FILE}\n")
        for key in ("host", "email", "token"):
            value = cfg["jira"].get(key, "(not set)")
            # mask the token so it's not shown in full
            if key == "token" and value != "(not set)":
                value = value[:6] + "..." + value[-4:]
            print(f"  {key:<6} = {value}")
        return

    key = args[0].lower()
    if key not in valid_keys:
        sys.exit(f"ERROR: Unknown config key '{key}'. Valid keys: {', '.join(sorted(valid_keys))}")

    # timelog config <key>  →  show one value
    if len(args) == 1:
        value = cfg["jira"].get(key, "(not set)")
        if key == "token" and value != "(not set)":
            value = value[:6] + "..." + value[-4:]
        print(f"{key} = {value}")
        return

    # timelog config <key> <value>  →  set value
    value = args[1].strip()
    if key == "host":
        value = value.rstrip("/")
        if not value.startswith("https://"):
            sys.exit("ERROR: host must start with https://")

    cfg["jira"][key] = value
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        cfg.write(f)

    if key == "token":
        display = value[:6] + "..." + value[-4:]
    else:
        display = value
    print(f"Saved: {key} = {display}  ({CONFIG_FILE})")


USAGE = """\
Usage:
  timelog tasks [--project <PROJECT>]                     -- list your assigned tasks
  timelog start <TICKET-ID> "<description>" [OPTIONS]    -- start timer

Options for start:
  --status "<status>"                                     -- update ticket status
  --started "<time>"                                      -- custom start time (14:30 or "1.5h ago")
  --replace                                               -- replace running timer

Other commands:
  timelog done                                            -- stop and post to JIRA
  timelog status                                          -- show running timer
  timelog cancel                                          -- discard timer
  timelog today                                           -- show today's worklogs
  timelog week                                            -- show this week's worklogs
  timelog config                                          -- show current config
  timelog config <key>                                    -- show one value (host, email, token)
  timelog config <key> <value>                            -- set a value

Examples:
  timelog tasks                                           -- show all your tasks
  timelog tasks --project WRSHALLOWFORD                   -- show WRSHALLOWFORD tasks only
  timelog start 1 "Working on this"                       -- start timer for task #1
  timelog start PROJ-123 "Task" --started 14:30           -- start at 2:30 PM today
  timelog start PROJ-123 "Task" --started "1.5h ago"      -- start 1.5 hours ago
  timelog start PROJ-456 "New task" --replace             -- auto-replace running timer
"""

def main():
    """Parse command-line arguments and dispatch to appropriate command handler."""
    args = sys.argv[1:]
    if not args:
        print(USAGE)
        sys.exit(0)
    cmd = args[0].lower()
    if cmd == "start":
        if len(args) < 3:
            sys.exit('Usage: timelog start <TICKET-ID-or-NUMBER> "<description>" [--status "<status>"] [--started "<time>"] [--replace]')
        ticket = args[1].upper()
        description = args[2]
        status = None
        start_time = None
        replace = False

        # Parse optional flags
        i = 3
        while i < len(args):
            if args[i] == "--status" and i + 1 < len(args):
                status = args[i + 1]
                i += 2
            elif args[i] == "--started" and i + 1 < len(args):
                start_time = args[i + 1]
                i += 2
            elif args[i] == "--replace":
                replace = True
                i += 1
            else:
                i += 1

        cmd_start(ticket, description, status=status, start_time_str=start_time, replace=replace)
    elif cmd == "done":
        cmd_done()
    elif cmd == "status":
        cmd_status()
    elif cmd == "cancel":
        cmd_cancel()
    elif cmd == "tasks":
        project = None
        if len(args) > 1 and args[1] == "--project" and len(args) > 2:
            project = args[2]
        cmd_tasks(project=project)
    elif cmd == "today":
        cmd_today()
    elif cmd == "week":
        cmd_week()
    elif cmd == "config":
        cmd_config(args[1:])
    else:
        print(f"Unknown command: {cmd}\n")
        print(USAGE)
        sys.exit(1)


if __name__ == "__main__":
    main()
