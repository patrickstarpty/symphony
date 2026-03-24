---
name: commit
description: Use when current changes are ready to commit or when a commit message needs to be prepared from staged work
---

# Commit

Create a clean git commit that matches the actual diff and records what changed, why, and how it was validated.

**Core principle:** Commit only intentional changes, and make the message explain the diff.

**Announce at start:** "I'm using the commit skill to prepare a clean commit."

## Workflow

### 1. Inspect the scope

```bash
git status --short
git diff --stat
git diff --staged --stat
```

- Review unstaged, staged, and untracked files before writing the message.
- If unrelated files are mixed in, fix the index before committing.
- Sanity-check new files so you do not commit logs, caches, build outputs, or session artifacts.

### 2. Stage the intended change

```bash
git add -A
git diff --staged
```

- If `git add -A` is too broad, stage files selectively instead.
- The staged diff must match the work you are about to describe.

### 3. Choose the commit message shape

- Use a conventional type prefix when it fits: `feat`, `fix`, `refactor`, `docs`, `test`, `chore`.
- Add an optional scope when it clarifies the area: `fix(orchestrator): ...`.
- Keep the subject imperative, no trailing period, and ideally <= 72 characters.

### 4. Write the body

Include:

- `Summary:` what changed
- `Rationale:` why it changed
- `Tests:` commands run, or an explicit note if not run
- `Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>`

### 5. Commit with a literal message file

```bash
tmp_msg=$(mktemp)
cat > "$tmp_msg" <<'EOF'
fix(scope): short subject

Summary:
- ...
- ...

Rationale:
- ...

Tests:
- make -C elixir all

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>
EOF

git commit -F "$tmp_msg"
rm -f "$tmp_msg"
```

## Before committing

- The message matches the staged diff.
- No unrelated files are included.
- Validation status is truthful.
- If separate unstaged work remains, do not pretend the commit covers it.

## Red flags

- Do not use `git commit -am` blindly.
- Do not summarize work that is not staged.
- Do not hide missing validation.
- Do not commit temporary debug output, local env files, or generated noise unless intentionally required.
