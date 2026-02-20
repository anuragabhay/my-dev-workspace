# Git Workflow Skill

## When to Use
Use this skill for any task involving:
- Creating or switching git branches
- Making commits and pushing
- Creating or merging pull requests
- Resolving merge conflicts or rebase issues
- Parallel branch workflows (multiple engineers)
- Post-merge cleanup

## Key Procedures

### Feature Branch Flow
1. Start from fresh staging: `git checkout staging && git fetch origin && git reset --hard origin/staging`
2. Create branch: `git checkout -b feature/my-feature`
3. Make changes, commit, push: `git push -u origin feature/my-feature`
4. Create PR: `gh pr create --base staging --head feature/my-feature --title "..." --body "..."`
5. Merge PR (squash): `gh pr merge --squash --delete-branch`
6. Cleanup: `git checkout staging && git fetch origin && git reset --hard origin/staging`
7. Delete local branch: `git branch -D feature/my-feature`

### Conflict Resolution
1. Rebase onto staging: `git fetch origin && git rebase origin/staging`
2. Resolve conflicts or `git rebase --skip` for already-applied commits
3. Verify changes: `git diff origin/staging...HEAD --stat`
4. Force push: `git push --force-with-lease origin feature/xxx`

### Parallel Work Merge
1. Each engineer on separate branch with separate files
2. Merge PRs one at a time on GitHub
3. Between each: `git fetch origin && git reset --hard origin/staging`
4. Delete each feature branch after its PR merges

## Rules Reference
See `.cursor/rules/git-workflow.mdc` for the full set of rules.

## Completion Criteria
- All feature branches deleted (local + remote)
- Local staging matches origin/staging exactly
- `git status` shows clean working tree
- No ahead/behind commits
