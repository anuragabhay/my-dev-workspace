# Git Branching Strategy

This document defines the branching model for the repository. All agents and contributors must follow it.

## Branch roles

- **staging** = **default branch**. Day-to-day development happens on `staging`. This is the repository default branch. Feature branches merge here; all integration and testing happens on `staging`.

- **master / main** = **production (releases only)**. This branch represents released, production-ready state. No direct pushes; updates only when releasing. Merge from `staging` to `master` only when there are many features of one type and a formal release is warranted—not for every batch of changes.

- **feature branches** = Short-lived branches for development. Branch **from** `staging`, do work, then merge **back to** `staging`. Do not merge feature branches directly to `master`.

## Rules

1. **Default branch = staging.** Staging is the default branch. All day-to-day work targets `staging`; new clones and PRs default to `staging`.

2. **Release to master only for releases.** Merge `staging` → `master` only when there are many features of one type and a formal release is warranted—not for every batch of changes. No direct merges to `master`; updates only via approved pull requests from `staging`.

3. **Feature workflow:** Create a feature branch from `staging` → implement → open PR into `staging` → merge to `staging`. Continue working on `staging`. When ready for a release (many features, formal release), open a PR from `staging` to `master` and follow the approval process.

---

## Agent workflow

Rules for automated agents (Orchestrator, Lead Engineer, Junior Engineers, etc.) when interacting with Git:

1. **Agents push to feature branches only.** Agents never push directly to `staging` or `master`. All work goes on a feature branch off `staging`.

2. **Pause after push.** After a subagent pushes a feature branch, the Orchestrator sets `User Intervention Required = Yes` in `PROJECT_WORKSPACE.md` and pauses. The Orchestrator outputs an "ACTION REQUIRED" message with the GitHub PR URL.

3. **User creates and merges PR.** The user (human) creates and merges the pull request on GitHub manually. Agents do not create or merge PRs.

4. **Sync after merge — never `git pull`.** After the user confirms the PR is merged, agents run:
   ```
   git checkout staging && git fetch origin && git reset --hard origin/staging
   ```
   Never use `git pull` after a squash merge — squash-merge rewrites history, causing divergent histories that `git pull` cannot reconcile.

5. **Agents never use `gh` CLI.** Agents do not use GitHub CLI (`gh`) for PR creation, closure, or any GitHub API operations. All GitHub operations are performed by the user.

6. **One feature branch per task/phase.** Each task or phase gets its own feature branch. Delete feature branches locally after the PR is merged.

7. **The Orchestrator never runs git commands.** The Orchestrator delegates all git operations (checkout, fetch, reset, commit, push, branch creation/deletion) to subagents (Lead Engineer, Junior Engineer 1, Junior Engineer 2). The Orchestrator only reads workspace state, decides the next task, and issues slash-command delegations.

---

## GitHub repository checklist (user action)

Configure the GitHub repository as follows. The Orchestrator and agents do **not** change GitHub settings; the user must perform these steps.

- [ ] **Branch protection for `master` (or `main`)**
  - Do not allow direct push to `master`; require pull requests.
  - Enable "Require a pull request before merging" for `master`.
  - Optionally: require status checks and/or required reviews.

- [ ] **Create `staging` branch**
  - Create a `staging` branch from the current `master` (or `main`) and push it to the remote so it exists on GitHub.

- [ ] **Default branch and merge rules**
  - Set **default branch = `staging`** (day-to-day work targets staging).
  - Configure merge rules (e.g. squash or merge commit) to match team preference and this strategy.

- [ ] **Required reviews (optional)**
  - If desired, require one or more approvals for PRs targeting `master` (and optionally for PRs targeting `staging`).

After completing the above, reply **"continue"** (or **"done"** or **"ready"**) in the workspace so the Orchestrator can proceed with Phase 1.3–1.4 and Phase 2. Release to `master` only when many features warrant a formal release—not for every batch.
