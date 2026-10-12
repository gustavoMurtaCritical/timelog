# Installation Guide for timelog

Complete step-by-step instructions for setting up timelog on your machine.

---

## Prerequisites

You need:
- **Windows 10 or later** (also works on Mac/Linux)
- **Python 3.8 or later** — [Download from python.org](https://www.python.org/downloads/)
- **JIRA account** with Personal Access Token

---

## Step 1: Install Python

1. Go to https://python.org/downloads
2. Download **Python 3.8 or later** (latest stable version recommended)
3. Run the installer
4. **IMPORTANT:** Check these boxes during install:
   - ✅ "Add Python to PATH"
   - ✅ "Install for all users"
5. Click **Install Now**
6. Click **Disable path length limit** (if prompted)

**Verify installation:**
```bash
python --version
# Should show: Python 3.x.x
```

---

## Step 2: Get timelog Files

**Option A: From a colleague**
1. Ask your colleague for the `timelog` folder
2. Copy it to a location like `C:\Users\<yourname>\scripts\timelog\`

**Option B: Clone/download**
1. Download all these files to a folder:
   - `timelog.py`
   - `timelog.bat`
   - `README.md`
   - `SETUP.md`
   - `CHANGELOG.md`

2. Place them in a folder, e.g.: `C:\Users\<yourname>\scripts\timelog\`

---

## Step 3: Add Folder to PATH

This lets you run `timelog` from anywhere.

**Open PowerShell as Administrator:**
1. Press `Windows Key + X`
2. Click **Windows PowerShell (Admin)**
3. Run this command (replace the path with your folder):
   ```powershell
   setx PATH "%PATH%;C:\Users\<yourname>\scripts\timelog"
   ```

4. **Close and reopen PowerShell** (important!)

**Verify it works:**
```bash
timelog
# Should show the usage message
```

---

## Step 4: Get JIRA Credentials

You need your JIRA username and a Personal Access Token.

**Get your token:**
1. Go to https://jira.critical.pt (or your JIRA instance)
2. Click your **profile picture** (top right)
3. Click **Settings**
4. Click **Personal Access Tokens** (left sidebar)
5. Click **Create token**
6. Give it a name like "timelog"
7. Make sure these permissions are enabled:
   - ✅ Search issues
   - ✅ Manage issues
   - ✅ Write work logs
8. Click **Create**
9. **Copy the token** (you won't see it again!)

---

## Step 5: Configure timelog

**In PowerShell**, run these three commands:

```bash
timelog config host https://jira.critical.pt
```

```bash
timelog config email your-jira-username
```

```bash
timelog config token <paste-your-token-here>
```

**Verify it worked:**
```bash
timelog config
```

You should see:
```
Config file: C:\Users\<you>\.timelog.cfg

  host  = https://jira.critical.pt
  email = your-username
  token = xxxxxx...xxxx
```

---

## Step 6: Test It Works

Try these commands:

```bash
# List your tasks
timelog tasks

# You should see your assigned JIRA tasks
```

If you get an error, see [Troubleshooting](#troubleshooting) below.

---

## Troubleshooting

### "timelog: command not found"
- **Cause:** Python not on PATH or folder not added to PATH
- **Fix:** Restart PowerShell and try again

### "Client must be authenticated (401 error)"
- **Cause:** Wrong email, token, or permissions
- **Fix:** 
  1. Check email: `timelog config email` (should match JIRA username)
  2. Regenerate token: Delete old token in JIRA, create new one
  3. Update token: `timelog config token <new-token>`

### "JIRA API error 404"
- **Cause:** Wrong JIRA host URL
- **Fix:** Check your JIRA URL. It should be `https://jira.critical.pt`
  ```bash
  timelog config host https://jira.critical.pt
  ```

### Python not found
- **Cause:** Python not installed or not on PATH
- **Fix:** 
  1. Check if Python is installed: `python --version`
  2. If not found, reinstall Python (remember to check "Add to PATH")
  3. Restart PowerShell after installing

---

## Next Steps

Once installed, see:
- **[README.md](README.md)** — Overview and features
- **[QUICKSTART.md](QUICKSTART.md)** — Common workflows
- **[SETUP.md](SETUP.md)** — Full command reference

---

## Getting Help

**If something doesn't work:**
1. Check Troubleshooting section above
2. Look at [SETUP.md](SETUP.md) for detailed command reference
3. Try: `timelog --help` or just `timelog`
4. Ask a colleague or check [CHANGELOG.md](CHANGELOG.md)

---

## What Gets Installed

After setup, you'll have:
- `timelog.cfg` in your home folder (`C:\Users\<you>\.timelog.cfg`) — Your config
- `timelog_state.json` in your home folder — Currently running timer (created automatically)
- `timelog_tasks_cache.json` in your home folder — Cached task list (created automatically)

None of these files contain sensitive data except your JIRA token. Keep your home folder secure.

---

## Uninstalling

To remove timelog:
1. Delete the `timelog` folder you copied
2. Remove from PATH:
   ```powershell
   # Open Settings > System > Environment Variables > Edit PATH
   # Remove the line pointing to timelog folder
   ```
3. Delete your config (optional):
   ```bash
   del C:\Users\<you>\.timelog.cfg
   ```

---

**Stuck?** Ask a colleague who's already using timelog, or contact the project maintainer.

Happy time tracking! ⏱️
