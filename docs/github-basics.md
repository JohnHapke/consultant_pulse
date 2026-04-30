# GitHub Basics

> For team members with no prior Git or GitHub experience.

---

## What is GitHub?

GitHub is a platform that stores project files and tracks every change ever made to them.
Think of it like SharePoint — but with a complete history of who changed what, when, and why.
Changes can be compared, reviewed, and undone at any time.

The files live on GitHub (the server). You work on a **local copy** on your machine and
sync changes in both directions.

---

## Core Concepts

| Term | What it means |
|---|---|
| **Repository (Repo)** | The project folder on GitHub — contains all files and their full history |
| **Commit** | A saved snapshot with a short note describing what changed and why |
| **Clone** | Download the full repository to your computer for the first time |
| **Pull** | Get the latest changes from GitHub into your local copy |
| **Push** | Send your local changes up to GitHub |
| **Branch** | A parallel version of the project — used by developers to test changes safely. As a PMO team member you will work on the `main` branch only. |
| **Status** | A summary of what has changed locally since the last save |

---

## One-Time Setup

> Complete these steps once. After that, skip straight to **Daily Use**.

### 1 — Install Git

**Windows (PowerShell):**
Download from [https://git-scm.com/download/win](https://git-scm.com/download/win) and install with default settings.
Restart PowerShell after installation.

**WSL (Windows Subsystem for Linux):**
Git is usually pre-installed. Verify with:
```bash
git --version
```
If not installed:
```bash
sudo apt install git
```

### 2 — Tell Git who you are (once per machine)

Run in PowerShell **or** WSL — same command on both:
```
git config --global user.name "Firstname Lastname"
git config --global user.email "your@company.com"
```

---

## Daily Use

### Get a project for the first time

```powershell
# PowerShell
git clone https://github.com/JohnHapke/project-name.git
cd project-name
```

```bash
# WSL
git clone https://github.com/JohnHapke/project-name.git
cd project-name
```

> Run this once. After that, use `git pull` to get updates.
>
> **First-time authentication:** GitHub will ask you to log in when you first clone.
> Install [GitHub CLI](https://cli.github.com/) and run `gh auth login` — select HTTPS and log in via browser.
> This is a one-time step per machine.

---

### Get the latest version

Always run this before starting work — makes sure you have the most recent files.

```powershell
# PowerShell — navigate to the project folder first
cd C:\Users\yourname\projects\project-name
git pull
```

```bash
# WSL
cd ~/projects/project-name
git pull
```

---

### Open the project in VS Code

Once you are inside the project folder, open VS Code with:

```
code .
```

The `.` means "this folder" — VS Code opens with all project files in the sidebar.

> **PowerShell:** Works if VS Code is installed and you checked "Add to PATH" during setup.
> **WSL:** Works if you installed the [WSL extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-wsl) in VS Code. VS Code opens on Windows but reads files from WSL.
>
> If `code .` is not recognized: open VS Code manually, go to **View → Command Palette**, type `Shell Command: Install 'code' command in PATH` and run it. Then restart your terminal.

---

### See what has changed

```
git status
```
Shows which files have been modified, added, or deleted locally.

```
git log --oneline -10
```
Shows the last 10 commits — who saved what and when.

---

### Save and share a change

Four steps — always in this order:

```
git status                          # 1. Check what changed
git add filename.yaml               # 2. Mark the file(s) to save
git commit -m "short description"   # 3. Save a snapshot with a note
git push                            # 4. Send to GitHub
```

> **`git add .`** marks all changed files at once. Use with care — only if you intend to save everything shown by `git status`.

---

## Quick Reference

| What you want to do | Command |
|---|---|
| Download a project (first time) | `git clone <url>` |
| Get the latest version | `git pull` |
| Open project in VS Code | `code .` |
| See what has changed locally | `git status` |
| See recent saves by the team | `git log --oneline -10` |
| Mark a file for saving | `git add <filename>` |
| Save a snapshot | `git commit -m "description"` |
| Send changes to GitHub | `git push` |

---

## Common Error Messages

| Message | What it means | What to do |
|---|---|---|
| `Your branch is behind` | Someone else pushed changes since your last pull | Run `git pull` first, then try again |
| `Merge conflict` | Two people changed the same part of the same file | Do not try to fix this alone — ask the project lead |
| `Permission denied` | You are not authenticated or not added to the repo | Run `gh auth login` or ask the project lead for access |
| `Nothing to commit` | No local changes found | No action needed — your files are already up to date |
