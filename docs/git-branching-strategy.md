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
