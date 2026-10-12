# Setting Up Git Repository for timelog

Step-by-step guide to share timelog via GitHub (or GitLab, Bitbucket, etc.).

---

## Prerequisites

You need:
- **Git** installed on your machine ([download](https://git-scm.com/download/win))
- **GitHub account** (free at [github.com](https://github.com))
- **Command prompt or PowerShell**

---

## Step 1: Install Git

1. Go to https://git-scm.com/download/win
2. Download and run installer
3. Use default settings (click Next through installer)
4. Finish installation

**Verify:**
```bash
git --version
# Should show: git version 2.x.x
```

---

## Step 2: Configure Git

Set your identity (one-time setup):

```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@criticalsoftware.com"
```

Example:
```bash
git config --global user.name "Gustavo Murta"
git config --global user.email "gustavo.murta@criticalsoftware.com"
```

---

## Step 3: Create GitHub Repository

1. Go to https://github.com
2. **Sign in** to your account
3. Click **+** (top right) → **New repository**
4. Fill in:
   - **Repository name:** `timelog`
   - **Description:** `JIRA time tracking CLI tool - log work hours without manual entry`
   - **Public** (so team can access)
   - ✅ Add a README.md
   - Click **Create repository**

**Copy the repository URL** (you'll need it):
```
https://github.com/YOUR_USERNAME/timelog.git
```

---

## Step 4: Initialize Local Repository

Open PowerShell and navigate to your timelog folder:

```bash
cd "C:\Users\gamurta\OneDrive - CRITICAL SOFTWARE, S.A\Desktop\Claude access\Effort_logger"
```

Initialize Git:

```bash
git init
```

---

## Step 5: Add Files to Git

Stage all files:

```bash
git add .
```

Check what will be committed:

```bash
git status
```

You should see:
```
On branch master

Initial commit

Changes to be committed:
  new file:   .gitignore
  new file:   CHANGELOG.md
  new file:   INSTALL.md
  new file:   LICENSE
  new file:   QUICKSTART.md
  new file:   README.md
  new file:   SETUP.md
  new file:   SHARING.md
  new file:   timelog.bat
  new file:   timelog.py
  ...
```

---

## Step 6: Create Initial Commit

```bash
git commit -m "Initial commit: timelog v1.2.0 - JIRA time tracking CLI"
```

---

## Step 7: Connect to GitHub

Add the GitHub repository as remote:

```bash
git remote add origin https://github.com/YOUR_USERNAME/timelog.git
```

Replace `YOUR_USERNAME` with your GitHub username!

Verify:

```bash
git remote -v
```

---

## Step 8: Push to GitHub

Push your code:

```bash
git branch -M main
git push -u origin main
```

You may be prompted to login to GitHub - use your credentials.

---

## Step 9: Verify on GitHub

1. Go to https://github.com/YOUR_USERNAME/timelog
2. You should see all your files
3. The README.md should be displayed on the main page

**Success!** Your repository is live! 🎉

---

## Share Repository Link with Team

Copy your repository URL:
```
https://github.com/YOUR_USERNAME/timelog
```

Send to team with this message:

```
📦 timelog is now available on GitHub!

🔗 Repository: https://github.com/YOUR_USERNAME/timelog

⚡ Quick Start:
1. Clone: git clone https://github.com/YOUR_USERNAME/timelog
2. Read: INSTALL.md
3. Setup: Follow 10-minute installation
4. Use: timelog tasks

📚 Documentation:
- README.md - Overview
- INSTALL.md - Setup guide
- QUICKSTART.md - Daily use
- SETUP.md - Full reference

Questions? Check the docs or ask me!
```

---

## Future Updates

When you make changes:

```bash
# Stage changes
git add .

# Commit
git commit -m "Description of changes"

# Push to GitHub
git push origin main
```

Example commits:
```bash
git commit -m "Add --replace flag for auto-timer switching"
git commit -m "Fix timezone handling in custom start times"
git commit -m "Update documentation with examples"
```

---

## Team Members: How to Clone

Colleagues can clone your repository:

```bash
git clone https://github.com/YOUR_USERNAME/timelog
cd timelog
# Then follow INSTALL.md
```

---

## Common Git Commands

```bash
# Check status
git status

# View commit history
git log --oneline

# See changes since last commit
git diff

# Stage specific file
git add filename.py

# Stage everything
git add .

# Commit
git commit -m "Your message here"

# Push to GitHub
git push origin main

# Pull latest changes
git pull origin main
```

---

## Troubleshooting

### "fatal: not a git repository"
```bash
# Make sure you're in timelog folder
cd "path\to\timelog"
git init
```

### "Permission denied (publickey)"
- GitHub requires authentication
- First time: GitHub will open browser to login
- Or: [Set up SSH key](https://docs.github.com/en/authentication/connecting-to-github-with-ssh)

### "Repository already exists"
```bash
# If you get this error, remove git and try again
rm -r .git
git init
```

### Can't push
```bash
# Make sure remote is set
git remote -v

# Should show:
# origin  https://github.com/YOUR_USERNAME/timelog.git

# If not:
git remote add origin https://github.com/YOUR_USERNAME/timelog.git
```

---

## Next Steps

1. ✅ Create GitHub repository
2. ✅ Clone to your machine
3. ✅ Make initial commit
4. ✅ Push to GitHub
5. ✅ Share link with team
6. ✅ Team members clone & setup
7. ✅ Make updates, push regularly

Your timelog is now on GitHub! 🚀

---

## GitHub Tips

**Add collaborators:**
1. Go to Settings → Collaborators
2. Click "Add people"
3. Search for teammate's GitHub username
4. Send invite

**Enable Discussions:**
1. Settings → Features
2. ✅ Enable Discussions
3. Team can ask questions in Discussions tab

**Create Releases:**
1. Go to Releases
2. Click "Create a new release"
3. Tag version: `v1.2.0`
4. Add release notes
5. Attach files (ZIP with timelog)

---

**Ready to share globally?** Your GitHub link can be shared with anyone! 🌍
