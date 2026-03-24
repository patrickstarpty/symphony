---
name: pull
description: Use when syncing the current branch with its base branch (usually origin/main) via a merge-based update and resolving conflicts safely
---

# Pull

Sync the current branch with its base branch, usually `origin/main`. Use a merge, not a rebase, unless the user explicitly asks otherwise.

**Core principle:** Understand both sides of a conflict before resolving it.

**Announce at start:** "I'm using the pull skill to sync this branch with its base branch."

## Workflow

### 1. Verify working tree state

```bash
git status --short
```

- If local changes exist, commit them first with the `commit` skill or stash only if they are truly temporary.

### 2. Enable rerere

```bash
git config rerere.enabled true
git config rerere.autoupdate true
```

### 3. Fetch and sync the current branch

```bash
branch=$(git branch --show-current)
git fetch origin
git pull --ff-only origin "$branch"
```

If the current branch is the base branch itself, stop after the fast-forward pull.

### 4. If this is a feature branch, merge the base branch with better conflict context

```bash
git -c merge.conflictstyle=zdiff3 merge origin/main  # or origin/<base-branch>
```

### 5. If conflicts appear, resolve them deliberately

Start with:

```bash
git status
git diff --merge
```

Guidelines:

- Resolve one file at a time.
- Summarize what "ours" and "theirs" are trying to do before editing.
- Prefer minimal, intention-preserving merges.
- Preserve behavior and API contracts unless the conflict clearly changes them.
- For generated files, resolve source conflicts first, then regenerate.
- Ask the user only when there is no safe default and product intent cannot be inferred locally.
- If the repo uses a base branch other than `main`, adapt the same flow to that branch.

### 6. Finish the merge

```bash
git add <resolved-files>
git commit
```

Use `git merge --continue` instead of `git commit` if Git left the merge paused that way.

### 7. Validate after the merge

- Run targeted checks for the conflicted area immediately.
- For this repo, prefer `make -C elixir all` before the next push or handoff when feasible.

## Final checks

After resolving conflicts:

```bash
git diff --check
```

Then report:

- whether the merge was clean or conflicted
- the main files/conflicts resolved
- validation run afterward
