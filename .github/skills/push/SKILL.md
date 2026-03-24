---
name: push
description: Use when publishing current branch changes to origin and creating or updating the corresponding pull request
---

# Push

Push the current branch safely, then create or update its pull request so the title, body, and labels match the actual scope.

**Core principle:** Publish only after validation, and keep PR metadata as accurate as the diff.

**Announce at start:** "I'm using the push skill to publish this branch and sync its PR."

## Prerequisites

- `gh auth status` succeeds.
- The current branch is the branch you intend to publish.

## Related skills

- `commit`: use first if the working tree still has uncommitted changes.
- `pull`: use when push is rejected because the branch is stale or non-fast-forward.

## Workflow

### 1. Confirm branch and validation state

```bash
git status --short
branch=$(git branch --show-current)
gh auth status
make -C elixir all
```

- If the working tree has uncommitted changes, use the `commit` skill before pushing.
- If `make -C elixir all` is too expensive for an intermediate push, run scope-appropriate checks first, but do not hand off the work until the full gate is green.

### 2. Push normally

```bash
git push -u origin HEAD
```

### 3. If push is rejected

- For non-fast-forward or stale-branch problems, use the `pull` skill, rerun validation, then push again.
- Use `--force-with-lease` only after intentional history rewriting.
- For auth, permission, or workflow restriction errors, surface the exact error instead of changing remotes or protocols as a workaround.

### 4. Ensure a PR exists

```bash
pr_state=$(gh pr view --json state -q .state 2>/dev/null || true)
```

- If no PR exists, create one.
- If the PR is open, update it.
- If the branch points to a closed or merged PR, create a new branch and open a new PR.

### 5. Write or refresh PR metadata

- Title should match the shipped outcome, not just the latest commit.
- Body must follow `.github/pull_request_template.md`.
- Refresh the PR body whenever scope changed.

### 6. Validate the PR body

```bash
tmp_pr_body=$(mktemp)
gh pr view --json body -q .body > "$tmp_pr_body"
(cd elixir && mix pr_body.check --file "$tmp_pr_body")
rm -f "$tmp_pr_body"
```

### 7. Ensure the PR has the `symphony` label

```bash
gh pr edit --add-label symphony
```

### 8. Return the PR URL

```bash
gh pr view --json url -q .url
```

## Suggested command flow

```bash
branch=$(git branch --show-current)
gh auth status
make -C elixir all
git push -u origin HEAD

tmp_pr_body=$(mktemp)
# Draft PR body from .github/pull_request_template.md into "$tmp_pr_body"

pr_state=$(gh pr view --json state -q .state 2>/dev/null || true)
if [ -z "$pr_state" ]; then
  gh pr create --title "<title>" --body-file "$tmp_pr_body"
else
  gh pr edit --title "<title>" --body-file "$tmp_pr_body"
fi

gh pr edit --add-label symphony
gh pr view --json url -q .url
rm -f "$tmp_pr_body"
```

## Red flags

- Do not create a PR with stale body text.
- Do not paper over failed validation.
- Do not switch remotes or protocols just to get around an auth problem.
- Do not use `--force`; prefer `--force-with-lease` when truly needed.
