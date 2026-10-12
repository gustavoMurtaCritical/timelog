# Sharing timelog with Your Team

This guide explains what to share and how to distribute timelog to colleagues.

---

## What To Share

### Required Files
These are **essential** — must be included:

- ✅ `timelog.py` — Main application (the core tool)
- ✅ `timelog.bat` — Windows launcher (makes it easy to run)

### Documentation Files
Users need these to understand and use timelog:

- ✅ `README.md` — Overview and features
- ✅ `INSTALL.md` — Step-by-step setup guide (most important!)
- ✅ `QUICKSTART.md` — Quick reference for daily use
- ✅ `SETUP.md` — Full command reference
- ✅ `CHANGELOG.md` — Version history

### Optional Files
Helpful for advanced users:

- ⭕ `test_timelog.py` — Unit tests (for developers only)

---

## How To Package & Share

### Option 1: ZIP File (Easiest)

**Create a ZIP file:**
1. Create a folder named `timelog-v1.2.0` (or current version)
2. Copy these files into it:
   ```
   timelog/
   ├── timelog.py
   ├── timelog.bat
   ├── README.md
   ├── INSTALL.md
   ├── QUICKSTART.md
   ├── SETUP.md
   └── CHANGELOG.md
   ```
3. Right-click folder → **Send to** → **Compressed (zipped) folder**
4. Rename to: `timelog-1.2.0.zip`

**Share the ZIP file via:**
- Email attachment
- File share (OneDrive, SharePoint, etc.)
- Team chat (Slack, Teams, etc.)

**User receives it and:**
1. Extracts the ZIP
2. Follows [INSTALL.md](INSTALL.md)

---

### Option 2: Shared Folder (Best for Team)

**Set up a shared location:**
1. Create folder: `\\server\shared\tools\timelog\` (or your network path)
2. Copy all files there
3. Share the network path with the team

**Users access it:**
```bash
# Copy to their machine
copy \\server\shared\tools\timelog C:\Users\<name>\scripts\timelog

# Then follow INSTALL.md
```

---

### Option 3: Repository (Best for Long-term)

If your team uses Git/GitHub:

```bash
# Create repo
git init timelog
git add .
git commit -m "Initial timelog release v1.2.0"
git push

# Users clone it
git clone https://github.com/yourorg/timelog
cd timelog
# Follow INSTALL.md
```

---

## Distribution Checklist

Use this checklist when sharing:

### Before Sharing
- [ ] All documentation files present and up-to-date
- [ ] Test locally: Unzip/copy files to a test machine
- [ ] Verify `timelog --help` works
- [ ] Verify `timelog tasks` works (with valid credentials)
- [ ] Check that INSTALL.md has correct JIRA host URL
- [ ] Update CHANGELOG.md if this is a new version

### When Sharing
- [ ] Use clear naming: `timelog-1.2.0.zip` (version included)
- [ ] Include a cover message explaining:
  - What timelog is
  - What it requires (Python 3.8+)
  - Where to get help (point to INSTALL.md)
  - How long setup takes (~10 minutes)

### Sample Cover Message

```
Subject: timelog - JIRA Time Tracking Tool

Hi team,

I'm sharing a tool I created to simplify time tracking in JIRA:

📋 What is timelog?
A command-line tool to start/stop work timers and post time to JIRA 
automatically. No more manual worklogs!

⚡ Quick start:
1. Extract the ZIP file
2. Follow INSTALL.md (takes ~10 minutes)
3. Run: timelog tasks
4. Run: timelog start <TICKET> "<description>"

✅ What you need:
- Windows 10+ (or Mac/Linux)
- Python 3.8+ (free)
- JIRA account

📚 Documentation:
- README.md — Overview
- INSTALL.md — Setup guide (start here!)
- QUICKSTART.md — Common commands
- SETUP.md — Full reference

❓ Questions? Check INSTALL.md troubleshooting or ask me.

Happy time tracking!
```

---

## System Requirements to Share

Make sure recipients know they need:

```
Minimum Requirements:
- Windows 10+ (macOS 10.14+, Linux)
- Python 3.8 or later (free from python.org)
- JIRA account access
- 10 minutes to set up

Internet:
- Connection to JIRA server required
- Personal Access Token needed (get from JIRA)
```

---

## Version Management

When you update timelog:

1. **Test thoroughly:**
   ```bash
   python -m unittest test_timelog -v
   ```

2. **Update CHANGELOG.md:**
   ```
   ## [1.2.0] — 2026-10-12
   
   ### Added
   - Custom start times
   - Auto-replace timer
   - Project filtering
   ```

3. **Create new ZIP:**
   - Name it with version: `timelog-1.2.0.zip`
   - Update cover message with what's new

4. **Share update:**
   - Announce to team with changelog highlights
   - Keep old versions for reference

---

## After Distribution

### Support Your Users

Expect these questions:

**Q: "timelog command not found"**
A: See INSTALL.md Troubleshooting → PATH setup

**Q: "How do I...?"**
A: Check QUICKSTART.md or SETUP.md

**Q: "I got an error"**
A: See INSTALL.md Troubleshooting section

**Q: "Can we add feature X?"**
A: Feature requests welcome! Document and share

### Feedback Loop

- Ask users for feedback after 1 week
- Document common issues in INSTALL.md
- Update tools based on feedback
- Share improvements with the team

---

## Distribution Scenarios

### Scenario 1: Small Team (5-10 people)
1. Create `timelog-1.2.0.zip`
2. Email to team with cover message
3. Offer to help with setup if needed

### Scenario 2: Medium Team (10-50 people)
1. Set up shared folder on network
2. Send email with link and cover message
3. Schedule optional "setup help" session
4. Document common issues in INSTALL.md

### Scenario 3: Large Organization (50+ people)
1. Set up Git repository
2. Create wiki/documentation page
3. Publish announcement in team channels
4. Offer training session
5. Designate "power users" for support

---

## Quick Share Links

When sharing, include these key links:

```
📖 Documentation:
- Start here: INSTALL.md (setup guide)
- Daily use: QUICKSTART.md (quick reference)
- Full reference: SETUP.md (all commands)
- Overview: README.md (features & how it works)

❓ Help:
- Setup issues → INSTALL.md Troubleshooting
- Command questions → QUICKSTART.md or SETUP.md
- Version history → CHANGELOG.md
```

---

## Sharing Checklist (Print & Use)

```
☐ Package timelog files into ZIP
☐ Name it: timelog-1.2.0.zip (with version)
☐ Test ZIP by extracting to test machine
☐ Verify all documentation files are included
☐ Create cover message (use template above)
☐ Verify INSTALL.md has correct JIRA host URL
☐ Check Python requirement (3.8+) is documented
☐ Share ZIP via email/share/repo
☐ Offer support for setup questions
☐ Collect feedback after 1 week
☐ Document any issues found
```

---

## Version History for Distribution

Keep track of what you're sharing:

| Version | Date | What's Included | Notes |
|---------|------|-----------------|-------|
| 1.0.0 | 2026-06-26 | Basic timer + JIRA posting | Initial release |
| 1.1.0 | 2026-09-11 | Tests + docs + daily reports | Added task selection |
| 1.2.0 | 2026-10-01 | Custom times + auto-replace | Current version |

---

## Next Steps for Sharing

1. **Prepare:** Create `timelog-1.2.0.zip` file
2. **Test:** Extract & verify on clean machine
3. **Document:** Customize cover message
4. **Share:** Email to team with INSTALL.md link
5. **Support:** Help with questions first week
6. **Feedback:** Collect usage feedback
7. **Improve:** Update tools based on feedback
8. **Iterate:** Share improvements with team

---

**Ready to share?** Follow the checklist above, send the ZIP, and enjoy your team's faster time tracking! 🚀
