# CLAUDE.md

<!-- shared-rules 2026-11-03: start -->
## Shared rules
- **This is a learning project.** The user is a beginner at infra and devops: explain each decision, why it was chosen, and the alternatives.
- **Never make up data.** If you can't check something, say so.
- **When unsure, stop and ask** instead of guessing or changing things.
- **Suggest improvements**, as suggestions: alternatives, idioms, best practices. Never apply them without approval.
- **Keep token use down**: concise answers, no restating what's established, no big artifacts unless asked.
- **Flag when the session is getting long**, and suggest a `/clear` at a natural break (after a commit, once the notes are up to date). Resuming relies on files (the branch, `git log`, the working notes), not on the chat history, so clearing often costs little.
- **Commits** follow Conventional Commits: a subject of about 70 characters, a blank line, then the details.
- **Docs use `<version>` placeholders**, never real version numbers; the real version lives only in the version file.
- **Keep it portable**: don't rely on this machine's setup (absolute home paths, WSL-only behaviour, tools installed only on the host). When something has to live outside the repo, say so: the repo's own prerequisites go in its `README`, machine-wide ones in `docs-hub`'s `machine-setup.md` (report them as a finding).
<!-- shared-rules: end -->

## What this repo is
The local dev environment for APE: a Docker Compose stack (Traefik, PHP-FPM + Nginx for the API, the Vue dev server, MySQL, phpMyAdmin, Dozzle) and `dev.py`, the CLI that
drives it (`dev up`, `dev composer`, `dev phpunit`, …). The app code isn't here: the API and front repos are cloned into `projects/` (see Read-only paths). Start with `README.md`.

Version file: `version.env` (`INFRA_VERSION`, SemVer, no `v`, committed). Compose passes it to the PHP container, and the API shows it. Bump it only when the prompt says so.

## Approval
- **The user makes every commit.** Never run `git commit`, `git push`, `git merge`, open a PR or delete a branch. Write the files for one step, explain them, suggest the commit message, then stop for review.
- **Changing files needs the user's OK.** Uncommitted changes are work waiting for review: don't redo or overwrite them, ask.
- The one exception: `/begin-chunk` may switch to `main`, run `git pull --ff-only`, and create the chunk's branch.

## Who runs what
- **The session may run** without asking: read-only git (`status`, `log`, `diff`, `show`, `git fetch` / `git fetch origin` / `git fetch --prune`, `git branch --show-current` / `--list` / `-a` / `-v`, `git check-ignore -q tmp/x`), reading files, and the one check: `python3 -m py_compile dev.py` (a syntax check; it writes `__pycache__/`, which is git-ignored). This list matches `.claude/settings.json`.
- **The user runs** every `docker` / `docker compose` command, every `dev` / `./dev.py` command (nearly all of them drive docker), and any `curl` against the stack. Give the exact command, say what it does, and ask for the output.
- Long check commands go in a git-ignored `tmp/checks.sh` for the user to read and run.

## Read-only paths
- `projects/` is git-ignored and holds **other repos**: the API (`projects/symfony-api/app`) and the front (`projects/ape-management-frontend/app`), each with its own sessions and `CLAUDE.md`. Read them when a change here needs it (how a wrapper is used, what a container expects); never write there.
- All writes stay in this repo.

## Workflow
Chunks use `/begin-chunk`, `/resume-chunk`, `/end-chunk` and `/close-chunk` (the steps live in the skills). The working notes go in `tmp/notes-<branch>.md` (git-ignored, never committed); `tmp/` must stay in `.gitignore`. One step per commit: `<type>(step N): <subject>`.

## Conventions
- The session writes the changes, after approval; the user reviews and commits them.
- Commands in docs run from the repo root (Compose looks for `docker-compose.yml` and `.env` there).
- `README.md` documents every `dev` command and alias: a change to `dev.py`'s commands or to `aliases` updates the README in the same step.
- `aliases` is the template for `~/.bash_aliases` (`dev aliases` fills in the path). Secrets stay in `.env` (git-ignored); new variables go into `.env.example` with a placeholder.
- Project Structure: conventions only, no file inventory (`ls` / `grep` instead).

## Gotchas
- `git` run inside `projects/...` acts on the **app repo**, not this one: use `git -C <path>` and check which repo you're in.
- The `dev` wrappers are bash aliases, so the session's shell can't run them (`type dev` → not found; fix in docs-hub's backlog). Hand them to the user anyway.
- `dev aliases` overwrites the **whole** `~/.bash_aliases` (it asks first).
- Raw `docker exec` into `symfony-php` needs `-u symfony`, or it creates root-owned files in the API repo.
- Data loss: `dev db-reset` and `dev nuke` delete the dev database (`dev db-dump` first). Never suggest them without saying so.
