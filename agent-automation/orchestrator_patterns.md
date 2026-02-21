# Orchestrator Patterns (Canonical Reference)

Canonical reference for workflow stages, role selection, and rules. The Orchestrator reads this document each cycle (with PROJECT_WORKSPACE.md) to decide next steps and delegate.

**Workflow and role definitions (stages, roles, decision order) are in YAML:** `agent-automation/workflow.yml`, `roles.yml`, `decisions.yml`. This document explains **why** stages exist, **when** to escalate, and **how** to write good delegation text.

---

## Stages

1. **Plan** — Decide what to do next from Implementation Plan and work log. Optionally delegate to PM for task breakdown or Architect for design options.
2. **Dev** — Implementation split into three parts: **Lead Engineer** (part 1), **Junior Engineer 1** (part 2), **Junior Engineer 2** (part 3). All three may run in parallel when the backlog supports it; delegate all three in the same response when three tasks exist.
3. **Review** — QA Reviewer, UI Reviewer, and Tester may run in parallel when applicable. Architect validates design/flow when needed.
4. **Merge** — After successful validation, one Merge step: Junior Engineer 1 or Junior Engineer 2 performs commit/push and work log update.
5. **Next steps** — After each stage (especially Review and Merge), Orchestrator reads PROJECT_WORKSPACE.md (Implementation Plan, Next Actions, Work Log), decides the next action, delegates to the concerned role, or writes ORCHESTRATION_COMPLETE when there is no remaining task.

---

## Orchestrator boundaries

You are a coordinator. You NEVER:
- Run shell commands (git, npm, pip, python, make, etc.)
- Edit, create, or delete files
- Write or modify code
- Execute any implementation step

You ONLY:
- Read workspace state (PROJECT_WORKSPACE.md, MCP tools)
- Decide the next task from the plan
- Delegate to the appropriate subagent via slash command
- Update Dashboard/Next Actions text (delegate file edits to a subagent if needed)

After user confirms a manual action ("done", "merged", "continue"):
1. Read workspace (git state, PROJECT_WORKSPACE.md, plan)
2. Decide the single next task
3. Delegate it to the correct subagent — do NOT execute it yourself

If you find yourself about to run a command or edit a file, STOP and delegate instead.
This rule has priority 0 — it overrides all other rules. See decisions.yml orchestrator_never_implements.

---

## After work done

After each stage (especially Review and Merge), the Orchestrator:

1. Reads PROJECT_WORKSPACE.md: Implementation Plan, Next Actions, last Work Log entries.
2. Decides the single immediate next action (one concrete task).
3. Either delegates that task to the concerned role (one slash command) or writes **ORCHESTRATION_COMPLETE** when there is no uncompleted task in the current scope.

---

## Role index

| Role              | Slash                | When to use                                                                 | Skill path (optional)                    |
|-------------------|----------------------|-----------------------------------------------------------------------------|------------------------------------------|
| Lead Engineer     | `/lead-engineer`     | Part 1 of dev split; core implementation, config, venv, main tests          | `.cursor/skills/lead-engineer/SKILL.md`   |
| Junior Engineer 1 | `/junior-engineer-1` | Part 2 of dev split; implementation, tests, docs, work log, commit/push    | `.cursor/skills/junior-engineer-1/SKILL.md` |
| Junior Engineer 2 | `/junior-engineer-2` | Part 3 of dev split; implementation, tests, docs, work log, commit/push    | `.cursor/skills/junior-engineer-2/SKILL.md` |
| Reviewer          | `/reviewer`          | Code review, quality review                                                 | `.cursor/skills/reviewer/SKILL.md`       |
| QA Reviewer       | (optional)           | QA-focused review                                                           | `.cursor/skills/qa-reviewer/SKILL.md`     |
| UI Reviewer       | (optional)           | UI/UX review                                                                | `.cursor/skills/ui-reviewer/SKILL.md`     |
| Tester            | `/tester`            | Test execution, test plans, QA                                              | `.cursor/skills/tester/SKILL.md`         |
| Architect         | `/architect`         | Design, "how to implement," architecture alignment, validation              | `.cursor/skills/architect/SKILL.md`      |
| PM                | `/pm`                | Task breakdown, acceptance criteria, scope                                  | (optional)                               |
| CTO               | `/cto`               | Technology, architecture approval                                            | (optional)                               |
| CFO               | `/cfo`               | Cost tracking and analysis only                                             | (optional)                               |

No "Intern" role or single "Junior Engineer"; only **Junior Engineer 1** and **Junior Engineer 2** with `/junior-engineer-1` and `/junior-engineer-2`.

---

## Parallel execution

- **Dev stage**: Orchestrator divides work into **three parts** and delegates to **Lead Engineer**, **Junior Engineer 1**, **Junior Engineer 2** in parallel; all three may receive slash commands in **one response** when the backlog supports three tasks.
- **Review**: QA Reviewer, UI Reviewer, and Tester may run in parallel when applicable; then one **Merge** (Junior Engineer 1 or 2: commit/push, work log).
- **Lead Engineer** for part 1; **Junior Engineer 1** and **Junior Engineer 2** for parts 2 and 3. Respect per-role concurrency from roles.yml if defined.

---

## MCP usage

- `get_pending_orchestrator_prompt` — at cycle start; if non-empty, execute as run-cycle instruction.
- `get_workspace_status` — overall status, pending approvals, blockers, phase.
- `get_workflow_config` — (if available) reads workflow.yml, roles.yml, decisions.yml; returns workflow stages, role list with slash commands; use for current-stage logic.
- `check_my_pending_tasks(role="Role Name")` — pending tasks for that role (e.g. "Lead Engineer", "Junior Engineer 1", "Junior Engineer 2", "Reviewer", "Tester", "Architect").
- `get_my_role_tasks(role)` — all tasks for a role (for context).
- `mark_task_complete(task_id, role)` — when a task is done (if the automation system uses task IDs).
- `get_role_guidance(role)` — (if available) returns role guidance from `.cursor/skills/<role>/SKILL.md` or `.cursor/agents/<role>.md`; Orchestrator may call when deciding delegation.
- `list_roles()` — (if available) returns list of role names and one-line "when to use"; includes Junior Engineer 1 and Junior Engineer 2 (no single "Junior Engineer" or "Intern").
