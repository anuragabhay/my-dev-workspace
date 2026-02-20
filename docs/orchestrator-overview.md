# Orchestrator Overview

Quick reference for all agents: what the Orchestrator does, when to plan vs delegate vs stop, where to read state, and workspace boundaries.

---

## 1. Purpose

The **Orchestrator** coordinates subagents. It:

- Uses **PROJECT_WORKSPACE.md** and **MCP** as the single source of truth for status and next steps.
- **Does not implement**—it decides what to do next and delegates.
- Delegates to: **Lead Engineer**, **Junior Engineer 1**, **Junior Engineer 2**, **Reviewer**, **Tester**, **Architect**.

---

## 2. When to plan vs delegate vs ORCHESTRATION_COMPLETE

| Action | When |
|--------|------|
| **Plan** | For non-trivial work: output a short "Plan: 1. … 2. …" then delegate. |
| **Delegate** | Issue slash commands for the **next concrete task(s)** (e.g. `/lead-engineer …`, `/junior-engineer-1 …`, `/junior-engineer-2 …`). |
| **ORCHESTRATION_COMPLETE** | **Only** when there is **no remaining task** in the current scope—not after every single task. |

---

## 3. Where to read state

- **Dashboard** — In PROJECT_WORKSPACE.md (User Intervention, Pending Approvals, Last Updated).
- **Next Actions** — In PROJECT_WORKSPACE.md.
- **Work log** — **Recent Work Log** in PROJECT_WORKSPACE.md and **agent-automation/work_log.json**.
- **Implementation Plan / Phase checklist** — In PROJECT_WORKSPACE.md (current phase and next uncompleted items).

---

## 4. Workspace boundaries

- Orchestrator and all subagents use the **same repo**.
- For **parallel runs**, each agent uses a **dedicated worktree**; merge back to main when done.
- Subagents run in their **assigned root/worktree** so work persists.
