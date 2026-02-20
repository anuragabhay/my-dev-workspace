# Multi-Agent Autonomous Development Workspace - YouTube Shorts Generation Pipeline

**Purpose**: Shared workspace for agent collaboration. Agents work autonomously, request approvals from senior roles via this document, and only escalate to user for financial/phase decisions. **Pilot** = Claude Pilot (code-quality tool from the plan: formatting, linting, type-checking, TDD).

**Document Version**: 1.0 (Workspace)  
**Created**: 2024  
**Last Updated**: 2024-01-15 16:00 UTC by SYSTEM

---

## 📊 Project Status Dashboard

**Overall Status**: 🟡 In Progress  
**Current Phase**: Phase 1 - Project Setup & Foundation (In Progress)  
**Last Updated**: 2026-02-20 by Orchestrator  
**Active Agents**: Lead Engineer, Junior Engineer 1, Junior Engineer 2, Reviewer, Tester, Architect, PM, CTO, CFO  
**Pending Approvals**: 0  
**Blockers**: Staging branch protection blocks direct push; PR required.  
**Next Actions**: **Step 0 — BLOCKED:** All work committed and pushed to `step0-merge`. Staging has branch protection (requires PR). **User action:** Create PR `step0-merge` → `staging` at https://github.com/anuragabhay/my-dev-workspace/pull/new/step0-merge and merge. After merge, proceed with Task A (Web UI) and Task B (platform-agnostic) in parallel.  
**User Intervention Required**: Yes — Merge PR step0-merge → staging to complete Step 0.

---

## 📌 Step 0: Merge to Staging (in progress)

**Status:** Committed and pushed to `step0-merge`. Stale branches `feature/ui`, `feature/platform-agnostic` deleted.

**Done:**
- ✅ All modified and new files committed (staging config, retry utility, CLI enhancements, service updates, branching docs)
- ✅ Pushed to `origin/step0-merge` (direct push to staging blocked by branch protection)
- ✅ Deleted `feature/ui` and `feature/platform-agnostic` locally

**Blocked:** Staging requires PR. Create PR at https://github.com/anuragabhay/my-dev-workspace/pull/new/step0-merge (base: staging), merge, then Step 0 complete. Task A and B blocked until then.

---

## 🚀 Git Branching Strategy — Phase 3.2: Complete

**Status:** ✅ Phase 3.2 complete. No publish to master for this batch. Staging is the default branch; release to master only when many features warrant a formal release (see `docs/git-branching-strategy.md`).

**Completed:**
- ✅ Phase 1.1: Git branching strategy documented (`docs/git-branching-strategy.md`)
- ✅ Phase 1.2: GitHub branch protection configured (user completed)
- ✅ Phase 1.3: Staging branch created locally and pushed to origin
- ✅ Phase 1.4: Staging environment config created (`.env.example.staging`, `config.example.staging.yaml`, config loader supports `ENV=staging`)
- ✅ Phase 2.1: UI workstream (feature/ui) — rich library, colored output, progress indicators, formatted displays
- ✅ Phase 2.2: Platform-agnostic workstream (feature/platform-agnostic) — retry utility, enhanced pipeline, improved ElevenLabs service
- ✅ Phase 3.1: Integration review complete — UI wired into CLI, retry wired into services, `rich` added to requirements.txt
- ✅ Phase 3.2: Documented default branch = staging, release to master only for releases. Continuing work on staging.

---

## 📝 Recent Work Log (last 10)

### [2026-02-20 08:43 UTC] [Junior Engineer 1] [Merge feature/ui to staging] [COMPLETED]
Merged UI enhancements (rich library, colored output, progress indicators) to staging. Reviewer approved. Branches were already in sync (staging and feature/ui pointing to same commit 8d883a4). Verified merge status and pushed staging to origin.

### [2026-02-20 08:43 UTC] [Junior Engineer 2] [Merge feature/platform-agnostic to staging] [✅ COMPLETED]
Merged platform-agnostic improvements (retry utility, enhanced pipeline, ElevenLabs service) to staging. Reviewer approved. Branch already synchronized with staging (no merge needed).

### [2026-02-20 17:30 UTC] [Architect] [Validate Cycle 2: test_config, openai_service docs, README Troubleshooting] [COMPLETED]
Validated test_config.py, openai_service docstrings and docs/API.md, README Troubleshooting; all OK. Hand off to Junior Engineer 1 for commit, push.

### [2026-02-20 16:45 UTC] [Orchestrator] [Dev plan cycle 2: three-way split completed] [COMPLETED]
Delegated Part 1 (Lead: config tests test_config.py), Part 2 (JE1: openai_service docstrings + docs/API.md), Part 3 (JE2: README Troubleshooting). All delivered. Next: Architect validate then Merge.

### [2026-02-20T16:30:00Z] [Lead Engineer] [Add unit tests for src/utils/config.py (tests/test_config.py)] [COMPLETED]
tests/test_config.py: 13 pytest tests for get_config, validate_env, validate_config, load_env, load_config (mocked env / tmp .env and YAML; no real API keys). All 13 passed. Added test_load_env_with_tmp_env_file and test_get_config_valid_env_and_config_returns_no_errors.

### [2026-02-20 17:00 UTC] [Junior Engineer 2] [Expand README Troubleshooting section (Phase 6)] [✅ COMPLETED]
Expanded youtube-shorts-generator/README.md Troubleshooting: missing/invalid .env (OPENAI_API_KEY, Runway KEY/SECRET), config errors (timeouts, cost.target_per_video, paths), health check failures, API errors (OpenAI, ElevenLabs, Runway) with remedies; added 'Where to look' table (stderr, health JSON, stdout logs, PROJECT_WORKSPACE.md).

### [2026-02-20 15:30 UTC] [Architect] [Validate config validation, Pilot rules, README] [COMPLETED]
Validated main.py config validation, .claude/rules, README setup; all OK. Hand off to Junior Engineer 1 for commit, push.

### [2026-02-20 15:00 UTC] [Orchestrator] [Dev plan cycle 1: three-way split completed] [COMPLETED]
Delegated Part 1 (Lead Engineer: config validation on startup), Part 2 (Junior Engineer 1: Pilot rules agent-guidelines.mdc + refs), Part 3 (Junior Engineer 2: README setup). All three delivered. Next: Architect validate then Junior Engineer 1 or 2 commit, push.

### [2026-02-20 16:00 UTC] [Junior Engineer 1] [Create custom Pilot rules for youtube-shorts-generator (Phase 1)] [✅ COMPLETED]
Updated .claude/rules/agent-guidelines.mdc to reference PROJECT_WORKSPACE.md (path from workspace root: PROJECT_WORKSPACE.md). Set alwaysApply: true; fixed role refs (Junior Engineer 1/2). Existing content-generation.mdc and video-quality.mdc already present.

### [2026-02-20 06:01 UTC] [Junior Engineer 2] [Complete README.md with setup instructions (Phase 6)] [✅ COMPLETED]
- Expanded youtube-shorts-generator/README.md Setup section: venv create/activate (macOS, Linux, Windows), pip install -r requirements.txt, .env from .env.example and required API keys, config.yaml from config.example.yaml, run health command, run generate command.\n- Deliverable: README setup instructions complete; work log updated.

Full log: agent-automation/work_log.json

To add an entry: run `python agent-automation/append_work_log.py --timestamp "..." --role "..." --task "..." --status "..." [--content "..."].` Then run with `--update-workspace` to refresh the recent 10 in this file.

**Next steps (after Phase 6 health tests added):** (1) Work log: run append_work_log with role Lead Engineer, task e.g. "Added pytest tests for src/utils/health.py (tests/test_health.py, N tests)", status COMPLETED, then --update-workspace. (2) Next Actions: set to next Phase 6 item (e.g. "Lead Engineer: Add README Troubleshooting/Configuration section") or, if ready to push: "Architect: Validate current changes. Then Junior Engineer 1 or 2: append work log, commit, push, --update-workspace." (3) Orchestrator: do not re-delegate "add unit tests for health.py"; pick next concrete task from Next Actions. If subagent returns with no deliverable for the same task, use smaller subtask, another role, or pause (avoid re-delegation loops).

---
## 🎬 Runway ML integration (current initiative)

**Goal:** Wire real Runway ML video generation into youtube-shorts-generator. Video step is currently a stub; we have Runway API credits and want to use them.

**Phase 1 – Research (Junior Engineer):** Look up Runway API/SDK for text-to-video (and image-to-video if relevant). Document: **auth** (we use `RUNWAYML_API_KEY` in .env; Runway docs may use `RUNWAYML_API_SECRET`), **supported models** (e.g. gen4.5 text-to-video), **task lifecycle** (create → poll or wait → get output URL), **output format**. Put a short summary here in PROJECT_WORKSPACE or in a short doc (e.g. `youtube-shorts-generator/docs/runway_api_research.md`) so Lead Engineer can implement.

**Phase 2 – Implementation (Lead Engineer, after research):** In youtube-shorts-generator: add Runway SDK if needed; implement real call in `src/services/runwayml_service.py` (text-to-video, Shorts-friendly ratio e.g. 768:1280, ~5s); poll or wait for task result; download video to `tmp/runway_output.mp4`. Keep using `RUNWAYML_API_KEY` from .env (or support both `RUNWAYML_API_KEY` and `RUNWAYML_API_SECRET`). Pipeline should produce a real Runway-generated video when the video agent runs. Update PROJECT_WORKSPACE work log when done.

**Research summary (to be filled by Junior Engineer):** See [youtube-shorts-generator/docs/runway_api_research.md](youtube-shorts-generator/docs/runway_api_research.md) for auth (KEY vs SECRET), models (gen4.5), task lifecycle (create→poll→output URL), and output format.

---
## ✅ Approval Requests & Responses

### ✅ Approved Approval #001
- **Requested By**: Architect
- **Requested From**: CTO
- **Date**: 2024-01-15 17:00 UTC
- **Type**: Technical Decision (Architecture Approval)
- **Request**: "Please review and approve system architecture design in Part 3: System Architecture section"
- **Priority**: High (blocks Lead Engineer implementation planning)
- **Status**: ✅ Approved by CTO
- **Response**: Architecture design is well-structured and aligns with approved technology stack. The Simple Agent Orchestration pattern with Python asyncio is appropriate for MVP. Key strengths: clear agent responsibilities, proper state persistence with SQLite, comprehensive error handling, and built-in cost tracking. Sequential execution for MVP is the right approach. Service layer abstraction provides good separation of concerns. Database schema is well-designed. Approved for implementation.
- **Decision**: ✅ Approved
- **Decision Date**: 2026-02-14 15:48 UTC
- **Escalation**: None (within CTO authority)

**Architecture Summary:**
- Simple Agent Orchestration pattern with Python asyncio
- 8 specialized agents (Research, Script, Uniqueness, TTS, Video, Composition, Quality, Publishing)
- SQLite-based message queue and state persistence
- Sequential execution for MVP
- Comprehensive error handling and cost tracking
- Service layer abstraction for external APIs

**Approval Types**:
- **Technical Decision**: Architect→CTO, Lead Engineer→Architect, Junior Engineer 1 or 2→Lead Engineer
- **Cost Decision**: CFO→User (ALL budget transactions require User approval)
- **Phase Transition**: CEO→User
- **Strategic Decision**: CEO→User

---

## 🔄 Agent Communication Protocol (MANDATORY)

### Communication Method
- **Primary**: This document (PROJECT_WORKSPACE.md)
- **Format**: Work Log entries, Approval Requests, Role Status sections
- **Frequency**: Check document before starting work, after completing work, when blocked

### Before Starting Work
1. **Check for automated tasks**: Check `/Users/anuragabhay/agent-automation/prompts/{your_role}_action.md` for pending automated tasks (see "Checking for Automated Tasks" below)
2. Read entire document (Dashboard, Work Log, Approval Requests, Role sections)
3. Check for pending approvals you need to respond to (if senior role)
4. Check for blockers or dependencies
5. Check if task is already in progress
6. Mark task as "🟡 IN PROGRESS" in your Role section
7. Add Work Log entry: [TIMESTAMP] [ROLE] [TASK] [🟡 IN PROGRESS]

### Checking for Automated Tasks

**Before Starting Any Work:**
1. **Check for tasks via MCP (Recommended)**: Use MCP tools to automatically check for pending tasks:
   - Call `@check_my_pending_tasks role="Your Role"` in Cursor
   - Returns structured JSON with pending tasks, approvals, and context
   - No manual file checking needed
2. **Fallback - Check prompt files**: If MCP is unavailable, check `/Users/anuragabhay/agent-automation/prompts/{your_role}_action.md`
   - If prompt file exists: Read and execute the task
   - Update PROJECT_WORKSPACE.md as instructed
   - System will track state automatically
3. **If no tasks found**: Proceed with normal workflow from PROJECT_WORKSPACE.md

**MCP Tools Available:**
- `check_my_pending_tasks(role)` - Get pending tasks for your role
- `get_workspace_status()` - Get overall workspace status
- `mark_task_complete(task_id, role)` - Mark task as complete
- `get_my_role_tasks(role)` - Get all tasks for your role

**Prompt File Naming Convention (Fallback):**
- CTO: `cto_action.md` or `cto_review.md`
- Architect: `architect_action.md` or `architect_design.md`
- Lead Engineer: `lead_engineer_action.md` or `lead_engineer_implement.md`
- CFO: `cfo_action.md` or `cfo_review.md`
- CEO: `ceo_action.md` or `ceo_approve.md`
- Product Manager: `pm_action.md` or `product_manager_action.md`
- Junior Engineer 1: `junior_engineer_1_action.md`
- Junior Engineer 2: `junior_engineer_2_action.md`
- Reviewer: `reviewer_action.md` (if used)
- Tester: `tester_action.md` (if used)

**Integration with Automation:**
- **MCP Server**: Provides programmatic access to automation system (preferred method)
- **Prompt Files**: File-based fallback for manual checking
- The automation system monitors PROJECT_WORKSPACE.md and generates tasks automatically
- MCP tools provide real-time task discovery without file polling
- The automation system tracks processed items to prevent duplicate triggers

### Role Assignment Protocol

**Setting Up Agent Chats:**

When creating a new Cursor chat for a specific role, assign the role explicitly:

1. **Name the chat** with the role name (e.g., "CTO", "Lead Engineer", "Architect")
2. **Give the chat this initial prompt:**
   ```
   You are the [ROLE]. Your role-specific prompt file location is: /Users/anuragabhay/agent-automation/prompts/{role}_action.md. Always check this file before starting any work. If a prompt file exists, read it and execute the task described. If no prompt file exists, proceed with normal workflow from PROJECT_WORKSPACE.md.
   ```

**Role-to-Prompt File Mapping:**

- **CTO**: `prompts/cto_action.md` or `prompts/cto_review.md`
- **Architect**: `prompts/architect_action.md` or `prompts/architect_design.md`
- **Lead Engineer**: `prompts/lead_engineer_action.md` or `prompts/lead_engineer_implement.md`
- **CFO**: `prompts/cfo_action.md` or `prompts/cfo_review.md`
- **CEO**: `prompts/ceo_action.md` or `prompts/ceo_approve.md`
- **Product Manager**: `prompts/pm_action.md`
- **Junior Engineer 1**: `prompts/junior_engineer_1_action.md`
- **Junior Engineer 2**: `prompts/junior_engineer_2_action.md`
- **Reviewer**: `prompts/reviewer_action.md` (if used)
- **Tester**: `prompts/tester_action.md` (if used)

**How It Works:**

1. Automation system generates role-specific prompt files based on workspace state
2. Each chat knows its role (from initial assignment)
3. Each chat checks its role-specific prompt file before starting work
4. Automation doesn't need to know which chat is which - it just generates prompts
5. Each chat is responsible for checking its own prompt file

**Example Setup:**

**CTO Chat Setup:**
```
You are the CTO. Your role-specific prompt file location is: /Users/anuragabhay/agent-automation/prompts/cto_action.md. Always check this file before starting any work.
```

**Lead Engineer Chat Setup:**
```
You are the Lead Engineer. Your role-specific prompt file location is: /Users/anuragabhay/agent-automation/prompts/lead_engineer_action.md. Always check this file before starting any work.
```

**Important Notes:**

- Each chat operates independently and checks its own prompt file
- Multiple chats can exist for the same role (though not recommended)
- The automation system generates prompts based on workspace state, not chat identity
- Role assignment is manual (you assign when creating the chat)
- This enables parallel work while maintaining role-specific task routing

### Requesting Approval (Junior → Senior)
1. Complete your work to best of ability
2. Add Approval Request in Approval Requests section
3. Format: Include what, why, impact, urgency
4. Mark your task as "🔄 PENDING APPROVAL" in Role section
5. Add Work Log entry with approval request
6. Wait for senior role response (check document periodically)
7. If urgent, note in request

### Responding to Approval (Senior → Junior)
1. Check Approval Requests section regularly
2. Review the work (check relevant document sections)
3. Make decision: ✅ Approved | ❌ Rejected | 🔄 Needs Revision
4. Add response in Approval Request
5. Update Work Log with decision
6. If approved, mark junior's task as "✅ APPROVED" in their Role section
7. If rejected, provide clear feedback for revision

### Autonomous Decision Authority
**You can make decisions without approval if:**
- **Junior Engineer**: Tasks assigned by Lead Engineer, documentation, research
- **Lead Engineer**: Implementation details, code structure (within approved architecture)
- **Architect**: System design patterns (within CTO guidelines)
- **CTO**: Technical decisions, tool selection (within budget)
- **CFO**: Cost tracking and analysis only (NO autonomous budget decisions)
- **PM**: Task prioritization, user story details (within MVP scope)
- **CEO**: Strategic decisions within approved vision, resource allocation

**You MUST request approval for:**
- **Junior Engineer**: Any code changes, architectural decisions
- **Lead Engineer**: Architecture changes, new dependencies, major refactors
- **Architect**: Technology stack changes, major design pattern changes
- **CTO**: Budget increases, new paid services, phase transitions
- **CFO**: ALL budget changes, cost optimizations, new subscriptions, API tier upgrades, any spending decisions
- **PM**: Scope changes, new features outside MVP
- **CEO**: Phase transitions, strategic pivots

### Escalation to User (ONLY FOR)
1. **Financial Decisions**: ALL budget transactions, cost optimizations, new paid services, subscription changes, API tier upgrades, any spending decisions
2. **Phase Transitions**: Moving from Architecture → Planning → Development → Testing → Deployment
3. **Strategic Pivots**: Major vision/scope changes
4. **Blockers**: Issues that cannot be resolved by any agent role

**Escalation Format**:
## 🚨 User Intervention Required

### [URGENT] Financial Approval Needed
- **Requested By**: [ROLE]
- **Date**: [TIMESTAMP]
- **Request**: [Description]
- **Rationale**: [Why needed]
- **Options**: [List options]
- **Recommendation**: [Preferred option]
- **Status**: ⏳ Waiting for User Decision

### Conflict Resolution
- **Task Ownership**: First agent to mark "🟡 IN PROGRESS" owns it
- **Disagreements**: Senior role makes final decision
- **Blocked Tasks**: Document blocker clearly, wait for resolution
- **Parallel Work**: Use dependency graph to identify parallelizable tasks

### Communication Etiquette
- Be specific: Include timestamps, file names, section references
- Be clear: State what you need, why, and impact
- Be timely: Respond to approval requests within 2 work cycles
- Be professional: Use role-appropriate language
- Update timestamps: Always update "Last Updated" when making changes

---

## 👥 Role Hierarchy & Decision Authority

### Hierarchy
```
User (Final Authority - ALL Budget Decisions)
    ↓
CEO (Strategic, Phase Transitions)
    ↓
CFO (Cost Tracking & Analysis Only - NO Budget Authority)
CTO (Technical Strategy, Architecture Approval)
    ↓
Architect (System Design, Patterns)
    ↓
Lead Engineer (Implementation, Code Structure)
    ↓
Product Manager (Requirements, Task Prioritization)
    ↓
Junior Engineer (Implementation, Documentation, Testing)
```

### Decision Authority Matrix

| Decision Type | Junior Engineer | Lead Eng | Architect | CTO | CFO | PM | CEO | User |
|--------------|--------|---------|-----------|-----|-----|----|-----|------|
| Code Implementation | ❌ | ✅ | ✅ | ✅ | - | - | - | - |
| Architecture Changes | ❌ | ❌ | ⚠️ | ✅ | - | - | - | - |
| Tech Stack Changes | ❌ | ❌ | ❌ | ✅ | - | - | - | - |
| Budget Decisions (ALL) | - | - | - | - | ❌ | - | ❌ | ✅ |
| Cost Tracking/Analysis | - | - | - | - | ✅ | - | - | - |
| Scope Changes | - | - | - | - | - | ⚠️ | ✅ | - |
| Phase Transition | - | - | - | - | - | - | ❌ | ✅ |
| Strategic Pivot | - | - | - | - | - | - | ❌ | ✅ |

✅ = Can decide autonomously  
⚠️ = Should consult senior but can decide  
❌ = Must request approval  
- = Not applicable

---

## 👨‍💼 CEO Status

**Current Status**: ✅ Vision Approved | 🟡 Monitoring Progress  
**Last Updated**: 2026-02-14 23:30 UTC  
**Pending Approvals to Review**: 0  
**Pending Approvals from Me**: 0

**Tasks:**
- [x] Define product vision (✅ 2024-01-15 12:00)
- [x] Set success metrics (✅ 2024-01-15 12:00)
- [x] Approve MVP scope (✅ 2024-01-15 12:00)
- [x] Architecture noted (✅ CTO approved #001 2026-02-14; CEO defers technical approval to CTO)
- [ ] Phase transition approval (⏳ Will request from User when Phase 1 complete and team proposes transition)

**Approval Requests I Need to Respond To:**
- None currently

**Decisions Made:**
- Vision approved: Autonomous MCP-based YouTube Shorts generation
- MVP scope approved: Local development, single video per execution
- Success metrics set: 30+ videos/month, <$5/video, 80%+ quality score
- Monitoring cost targets and progress

**Blockers**: None  
**Next Action**: Monitor Phase 1; approve/request User approval for phase transition when Lead Engineer completes Phase 1

---

## 💰 CFO Status

**Current Status**: ✅ Cost Analysis Complete | 🟡 Standing By for Development Cost Tracking  
**Last Updated**: 2026-02-14 23:20 UTC  
**Budget Authority**: NO autonomous decisions - ALL budget transactions require User approval. CFO can only track and analyze costs.  
**Current Monthly Budget**: $130-166 (within $200 target)

**Important**: CFO role is for cost tracking, analysis, and recommendations only. ALL actual budget decisions, spending approvals, and cost optimizations must be approved by the User. CFO cannot autonomously approve any spending, no matter how small.

**Tasks:**
- [x] Verify all API costs (✅ 2024-01-15 13:15)
- [x] Update cost breakdown (✅ 2024-01-15 15:00)
- [x] Correct RunwayML pricing (✅ 2024-01-15 15:00)
- [ ] Monitor actual costs during development (⏳ Waiting for development)
- [ ] Analyze cost optimization opportunities (⏳ Future - will recommend to User for approval)

**Approval Requests:**
- None currently

**Cost Analysis Completed:**
- Verified RunwayML pricing: $0.05/sec (~$0.75-3.00/video)
- Confirmed all costs within budget: $4.10/video (with buffer: <$5.00)
- Removed infrastructure costs (local development)
- **Note**: All cost analysis completed. No budget decisions made (requires User approval for any spending)

**Blockers**: None  
**Next Action**: Monitor costs during development phase, provide analysis and recommendations to User for any budget decisions

---

## 🏗️ CTO Status

**Current Status**: ✅ Architecture Approved | ✅ Automation System Operational  
**Last Updated**: 2026-02-14 15:48 UTC  
**Senior**: CEO (for phase transitions), User (for all budget decisions)  
**Junior**: Architect (reviews architecture)

**Tasks:**
- [x] Review technology decision matrices (✅ 2024-01-15 10:00)
- [x] Approve final technology stack (✅ 2024-01-15 10:00)
- [x] Review and setup automation system (✅ 2026-02-14 21:15)
- [x] Review architecture design (✅ 2026-02-14 15:48) - Approval #001
- [x] Approve architecture (✅ 2026-02-14 15:48) - Approval #001

**Approval Requests I Need to Respond To:**
- None (Approval #001 completed)

**Approval Requests I Made:**
- None (all technology decisions within authority)

**Decisions Made:**
- Approved technology stack: Python asyncio + SQLite, GPT-4, ElevenLabs, RunwayML, ChromaDB
- Confirmed local development only for MVP
- All decisions within budget authority
- Approved automation system for agent workflow automation
- Approved system architecture design (Approval #001) - Simple Agent Orchestration pattern approved for implementation

**Blockers**: None  
**Next Action**: Support Lead Engineer during implementation phase

---

## 🏛️ Architect Status

**Current Status**: ✅ Architecture Complete | 🟡 Supporting Implementation  
**Last Updated**: 2026-02-14 22:45 UTC  
**Senior**: CTO (for architecture approval)  
**Junior**: Lead Engineer (supports during implementation)

**Tasks:**
- [x] Review requirements (✅ 2024-01-15 17:00)
- [x] Design system architecture (✅ 2024-01-15 17:00)
- [x] Document agent interfaces and data flow (✅ 2024-01-15 17:00)
- [x] Request CTO approval (✅ 2024-01-15 17:00) - Approval #001
- [x] Receive CTO approval (✅ 2026-02-14 15:48) - Approval #001
- [x] Finalize architecture (✅ 2026-02-14 15:48) - Approved by CTO
- [ ] Support Lead Engineer during implementation (🟡 Active - available for design questions)

**Approval Requests I Need to Respond To:**
- None (no juniors requesting approvals yet)

**Approval Requests I Made:**
- Approval #001: Architecture review (✅ Approved by CTO on 2026-02-14 15:48 UTC)

**Implementation Support:**
- Architecture documentation complete and approved
- Available to answer design questions from Lead Engineer
- Will review any architecture changes if requested
- Monitoring implementation to ensure alignment with approved design

**Blockers**: None  
**Next Action**: Support Lead Engineer during Phase 1 implementation (project setup and foundation)

---

## 👨‍💻 Lead Engineer Status

**Current Status**: 🟡 Phase 6 code quality in progress (config tests done)  
**Last Updated**: 2026-02-20 16:30 UTC  
**Senior**: Architect (for design questions), CTO (for tech decisions)  
**Junior**: Junior Engineer (assigns tasks to)

**Tasks:**
- [x] Stop hook conditional for Orchestrator only (✅ 2026-02-15 01:10) - .cursor/hooks/stop_hook.py: payload from stdin, transcript check (parent Orchestrator/orchestrator.mdc), Dashboard parse, followup only when CONTINUE and not User Intervention
- [x] Phase 5: health check (✅ 2026-02-15 00:45) - src/utils/health.py, cmd_health() wired; JSON report (api_keys, disk, resources, DB, OpenAI, ElevenLabs, RunwayML, YouTube)
- [x] Root README and push (✅ 2026-02-15 00:25) - README.md at repo root, commit + push
- [x] Review architecture (✅ 2026-02-14 21:30) - Architecture approved by CTO
- [x] Create implementation plan (✅ 2026-02-14 21:30) - Comprehensive 7-week plan created
- [x] Set up project structure (✅ 2026-02-14 21:37) - Directory structure created, __init__.py files initialized
- [x] Define code organization (✅ 2026-02-14 21:37) - Structure matches approved architecture
- [x] Create .gitignore (✅ 2026-02-14 21:37) - Configured for Python, secrets, temp files
- [x] Create initial README.md (✅ 2026-02-14 21:37) - Setup instructions and overview
- [x] Set up Python virtual environment (✅ 2026-02-14 23:25) - venv created per README
- [x] Install core dependencies (✅ 2026-02-14 23:25) - requirements.txt + pip install
- [x] Cursor Subagents + Hooks – Orchestrator setup (✅ 2026-02-14 24:15) - orchestrator rule, 6 subagents, stop hook, ORCHESTRATOR_SETUP.md
- [x] Config templates and loader (✅ 2026-02-14 24:25) - config.example.yaml, .env.example, src/utils/config.py
- [x] Database schema – models, repository, migrations (✅ 2026-02-14 24:35)
- [x] Logging & cost_tracker (✅ 2026-02-14 24:38) - src/utils/logging.py, cost_tracker.py
- [x] Phase 2 BaseAgent (✅ 2026-02-14 24:40) - src/agents/base_agent.py
- [x] Phase 2 message_queue, state_manager, pipeline (✅ 2026-02-14 24:45)
- [x] Phase 3–5: services, 8 agents, CLI (✅ 2026-02-14 25:00)
- [x] Phase 6: unit tests for health.py (✅ 2026-02-15 02:25) - tests/test_health.py, 5 pytest tests
- [x] Phase 6: unit tests for config.py (✅ 2026-02-20 16:30) - tests/test_config.py, 13 pytest tests (get_config, validate_env, validate_config, load_env, load_config; no real API keys)
- [x] Phase 6: README Troubleshooting/Configuration (✅ 2026-02-15) - youtube-shorts-generator/README.md
- [x] Phase 6: one small polish or Architect validate → Junior Engineer push (✅ 2026-02-15)
- [ ] Configure Pilot rules for Python development (🟡 Next - Phase 1)
- [ ] Create custom rules integrating with PROJECT_WORKSPACE.md (🟡 Next - Phase 1)
- [ ] Train team on Pilot usage (if applicable) (⏳ Waiting for Pilot setup)
- [ ] Assign tasks to Junior Engineer (⏳ Waiting for project structure setup)

**Approval Requests I Need to Respond To:**
- None (no Junior Engineer tasks yet)

**Blockers**: None  
**Next Action**: Pick next task from Implementation Plan (Phase 2 tests, Phase 1 Pilot/config, or doc polish). Append work log + --update-workspace when done.  

---

## 📋 Product Manager Status

**Current Status**: ✅ Requirements Complete | 🟢 Standing By  
**Last Updated**: 2026-02-14 23:45 UTC

**Tasks:**
- [x] Define user stories (✅ 2024-01-15 11:00)
- [x] Create acceptance criteria (✅ 2024-01-15 11:00)
- [x] Refine requirements (✅ 2024-01-15 14:30)
- [x] Add missing user stories (✅ 2024-01-15 14:30)
- [ ] Create detailed task breakdown (🟡 Can start, no blocker)
- [ ] Create development roadmap (🟡 Unblocked—architecture approved; can start when needed)

**Blockers**: None  
**Next Action**: Standing by for task prioritization, acceptance-criteria clarifications, or task breakdown/roadmap; check MCP or pm_action.md for assigned tasks

---

## 🎓 Junior Engineer Status

**Current Status**: ⏳ Waiting for Assignment  
**Last Updated**: 2026-02-14 23:00 UTC  
**Senior**: Lead Engineer (all tasks require approval)

**Tasks:**
- [ ] Research video libraries (⏳ Waiting for Lead Engineer assignment)
- [ ] Research FFmpeg usage (⏳ Waiting for Lead Engineer assignment)
- [ ] Write documentation (⏳ Waiting for code)
- [ ] Test components (⏳ Waiting for implementation)

**Approval Authority**: None - all work requires Lead Engineer approval  
**Blockers**: No assignments yet  
**Next Action**: Wait for Lead Engineer to assign tasks; check MCP or junior_engineer_action.md for new tasks

---

## 📋 Task Tracking by Phase

### Phase 1: Architecture Design
**Status**: 🟡 Ready to Start | **Owner**: Architect | **Dependencies**: Requirements (✅), Technology Stack (✅)

**Tasks:**
- [ ] Architect: Review requirements (⏳ Ready)
- [ ] Architect: Design system architecture (⏳ Ready)
- [ ] Architect: Document agent interfaces (⏳ Ready)
- [ ] Architect: Document data flow (⏳ Ready)
- [ ] Architect: Request CTO approval (⏳ Waiting for design)
- [ ] CTO: Review architecture (⏳ Waiting for Architect)
- [ ] CEO: Final approval if needed (⏳ Waiting for CTO)

**Parallel Tasks**: None  
**Blockers**: None (Architect can start immediately)  
**Next Phase**: Implementation Planning (blocked by architecture approval)

### Phase 2: Implementation Planning
**Status**: ✅ Complete | **Owner**: Lead Engineer | **Dependencies**: Architecture (✅)

**Tasks:**
- [x] Lead Engineer: Review architecture (✅ 2026-02-14 21:30)
- [x] Lead Engineer: Create implementation plan (✅ 2026-02-14 21:30)
- [x] Lead Engineer: Set up project repo structure (✅ per Implementation Plan Phase 1)
- [x] Lead Engineer: Define code organization (✅ per Implementation Plan Phase 1)
- [ ] Lead Engineer: Install and configure Claude Pilot (🟡 Ready - Phase 1)
- [ ] Lead Engineer: Create custom Pilot rules for project (🟡 Ready - Phase 1)
- [ ] Lead Engineer: Integrate Pilot with workspace workflow (🟡 Ready - Phase 1)
- [x] Lead Engineer: Document Pilot usage (✅ 2026-02-15 - README Pilot section)
- [ ] Junior Engineer: Research libraries (⏳ Waiting for Lead assignment)

**Blockers**: None - Ready to start Phase 1 implementation

### Phase 3: Development
**Status**: ⏸️ Blocked | **Owner**: Lead Engineer + Junior Engineer | **Dependencies**: Implementation Plan (⏸️)

**Tasks:**
- [ ] TBD after implementation plan

**Blockers**: Implementation planning required

---

## ⚠️ Blockers & Issues

*No active blockers currently. All foundational work complete, ready for architecture design.*

### [RESOLVED] Blocker #000: Cost Verification
- **Resolved**: 2024-01-15 15:00
- **Resolution**: CFO verified all costs, corrected RunwayML pricing, confirmed within budget
- **Status**: ✅ Resolved

---

## 📌 Status Indicator Legend

- ✅ **COMPLETED/APPROVED**: Finished and approved
- 🟡 **IN PROGRESS**: Currently working
- 🔄 **PENDING APPROVAL**: Waiting for senior approval
- ⏸️ **BLOCKED**: Cannot proceed (dependency/issue)
- ⏳ **PENDING/WAITING**: Ready but waiting
- ❌ **REJECTED/CANCELLED**: Not approved or cancelled
- 🚨 **USER INTERVENTION**: Requires user decision

---

# Part 1: Project Foundation (Reference - Read Only)

*Foundational requirements. Update only if requirements change. All agents reference this.*

---

## Product Vision & Requirements

### Product Vision Statement
Build an autonomous MCP-based system that generates and publishes one high-quality YouTube Short daily, using AI-generated video content, with minimal human intervention.

### Success Metrics

**Primary KPIs (First 90 Days)**
- **Content Velocity**: 30+ videos published in first month (1/day target)
- **Quality Score**: 80%+ videos pass automated quality checks
- **Engagement**: Average 1,000+ views per video by month 3
- **Automation Rate**: 95%+ of videos published without manual intervention
- **Cost Efficiency**: <$5 per video generated (all-in cost)

**Leading Quality Indicators**
- **Script Coherence Score**: 85%+ (measured by semantic consistency, logical flow, readability)
- **Video Technical Quality**: 90%+ pass technical validation (resolution, frame rate, audio levels)
- **Policy Compliance**: 100% pass YouTube policy pre-checks (no copyright flags, appropriate content)
- **Sync Accuracy**: <200ms audio-video synchronization error
- **Content Uniqueness**: <30% semantic similarity to previous videos

**Cost Component Breakdown**
- **RAG/Research**: <$0.10 per video (vector DB queries + embeddings)
- **LLM Content Generation**: <$0.50 per video (script + metadata generation)
- **TTS/Voice Synthesis**: <$1.00 per video (voiceover generation, 30-60 seconds)
- **Video Generation**: <$2.50 per video (AI video generation, 15-60 seconds at $0.05/sec)
- **Storage & Processing**: $0 per video (local filesystem, FFmpeg free)
- **YouTube API**: $0 per video (free quota sufficient)
- **Infrastructure**: $0 per video (local development, no cloud costs)
- **Total Target**: <$4.10 per video (with 20% buffer: <$5.00 per video)

**Cost Alert Thresholds**
- **Warning**: Cost per video exceeds $4.00 (80% of budget)
- **Critical**: Cost per video exceeds $6.00 (120% of budget)
- **Monthly Budget Alert**: Total monthly cost exceeds $150 (30 videos × $5)
- **Component Alert**: Any single component exceeds 2x its target cost

---

## MVP Scope

**In Scope for MVP:**

**Core Functionality**
- Single video generation per execution
- Basic content research using RAG (3-5 topic suggestions)
- AI-generated script (15-60 seconds)
- Voice synthesis (single voice profile)
- Video asset generation/composition (single style)
- YouTube upload with metadata
- Manual execution trigger (CLI or API endpoint)

**Error Handling**
- **Retry Logic**: 
  - API calls: 3 retries with exponential backoff (1s, 2s, 4s)
  - Transient failures: Automatic retry for network errors, rate limits
  - Permanent failures: Log and fail gracefully with error message
- **Cost Logging**: 
  - Track API costs per execution
  - Log cost breakdown by component
  - Store cost history (last 30 executions)
- **Health Checks**:
  - **Health Check Command/Endpoint**: CLI command or API endpoint to check system health
  - **Checks Performed**:
    - API connectivity (test each API endpoint)
    - API key validity (verify keys are active and have quota)
    - Disk space availability (minimum 10GB free)
    - System resources (8GB RAM available, CPU cores)
    - YouTube channel access (OAuth token valid)
    - Database connectivity (SQLite accessible)
  - **Output**: JSON status report with pass/fail for each check
  - **Usage**: Run before execution to prevent failures

**Quality Control (Basic)**
- Technical validation (duration, resolution, audio levels)
- Content uniqueness check (semantic similarity to last 10 videos)
- Basic policy compliance (keyword filtering)

**Observability (Basic)**
- Structured logging (JSON format)
- Execution status tracking
- Error aggregation and reporting

**Configuration Management**
- **API Keys**: Environment variables (.env file) for all API keys
- **Settings**: YAML/JSON config file for system settings (timeouts, thresholds, etc.)
- **Validation**: Validate all API keys and settings on startup
- **Error Handling**: Clear error messages if configuration is invalid or missing
- **Security**: Never commit API keys to version control (.env in .gitignore)

**Data Persistence**
- **Database**: SQLite (local file, no setup required)
- **Stored Data**:
  - Execution history (status, timestamps, errors)
  - Cost logs (per execution, per component)
  - Video metadata (title, description, YouTube ID, publish date)
  - Content embeddings (for uniqueness checking)
  - Queue state (if using persistent queue)
- **Backup**: Optional export to JSON for backup/analysis

**Explicitly Deferred to Phase 2:**
- Daily automation (scheduling/cron)
- Multi-video generation (batch processing)
- Advanced analytics dashboard
- Content A/B testing framework
- Multiple voice profiles
- Multiple video styles/themes
- Advanced quality scoring (ML-based)
- Cost optimization features (caching, batching)
- User interface (web dashboard)
- Multi-channel publishing
- Content calendar planning
- Performance metrics dashboard
- **Deployment infrastructure** (Docker, VPS, Cloud services)

**Explicitly Deferred to Phase 3:**
- Real-time monitoring dashboard
- Advanced retry strategies (circuit breakers, fallback providers)
- Multi-language support
- Custom branding/watermarks
- Advanced analytics (engagement prediction, trend analysis)
- Content personalization
- Automated thumbnail generation
- SEO optimization engine

---

## User Stories

### Epic 1: Content Generation Pipeline

#### US-1.1: Content Research
- **As a** system agent
- **I want** to research trending topics using RAG
- **So that** I can generate relevant, engaging content ideas

**Acceptance Criteria:**
- RAG system queries vector database for trending topics
- Returns 3-5 content ideas with relevance scores >0.7
- Content ideas include title suggestions and key points
- **Content Freshness**: Topics must be from last 7 days (or evergreen)
- **Duplicate Prevention**: Exclude topics used in last 10 videos (semantic similarity <0.3)
- **Topic Diversity**: Ensure topics span at least 2 different categories
- **Relevance Threshold**: Minimum relevance score of 0.7 for inclusion
- Research completes within 30 seconds
- **Fallback**: If no suitable topics found, use curated fallback topics

#### US-1.2: Script Generation
- **As a** content generation agent
- **I want** to generate a 15-60 second script based on research
- **So that** the video has engaging, coherent narration

**Acceptance Criteria:**
- Script is 15-60 seconds when read at normal pace
- Script includes natural transitions and hooks
- Script aligns with YouTube Shorts format (vertical, engaging)
- Script generation completes within 60 seconds

#### US-1.3: Voice Synthesis
- **As a** video production agent
- **I want** to convert script to natural-sounding voiceover
- **So that** the video has professional narration

**Acceptance Criteria:**
- Voiceover matches script exactly
- Audio quality is clear and natural (no robotic tone)
- Audio length matches script duration
- Voice synthesis completes within 90 seconds

#### US-1.4: Content Uniqueness Validation
- **As a** quality control agent
- **I want** to validate content uniqueness against previous videos
- **So that** we avoid repetitive content and maintain channel variety

**Acceptance Criteria:**
- Compare generated script against last 10 published videos
- **Storage**: Store embeddings in SQLite database (see US-5.4: Data Persistence)
- Calculate semantic similarity using embeddings
- Reject content if similarity >30% to any previous video
- Log similarity scores for monitoring
- If rejected, trigger content regeneration with different topic
- Validation completes within 10 seconds
- **Exception**: Allow higher similarity (up to 40%) for series/sequels (configurable)

### Epic 2: Video Production

#### US-2.1: Video Asset Generation
- **As a** video production agent
- **I want** to generate or retrieve video assets matching the script
- **So that** the video has visual content synchronized with narration

**Acceptance Criteria:**
- Video assets are 9:16 aspect ratio (vertical, 1080x1920 minimum)
- Assets match script themes and timing
- Assets are high quality (1080p minimum, 30fps minimum)

**Asset Types (Specified):**
- **Primary**: AI-generated video (text-to-video or image-to-video)
- **Fallback 1**: Stock footage (free/paid stock video libraries)
- **Fallback 2**: Animated graphics (simple motion graphics, text animations)
- **Fallback 3**: Static images with motion effects (Ken Burns effect, zoom, pan)

**Scene Segmentation:**
- Break script into 3-5 scenes based on key points
- Generate/select assets for each scene
- Ensure visual consistency within scenes (color palette, style)
- Smooth transitions between scenes

**Visual Consistency Requirements:**
- Consistent color palette across scenes (within same video)
- Consistent style (realistic vs. animated vs. abstract)
- No jarring style transitions
- Text overlays use consistent font and positioning

**Fallback Strategy:**
- If AI video generation fails: Use stock footage
- If stock footage unavailable: Use animated graphics
- If all fail: Use static images with motion effects
- Log fallback usage for monitoring

**Asset Generation completes within 5 minutes (with fallback chain)**

#### US-2.2: Video Composition
- **As a** video production agent
- **I want** to combine voiceover, video assets, and text overlays
- **So that** I create a complete, polished video

**Acceptance Criteria:**
- Video duration matches voiceover length
- All elements are synchronized
- Video meets YouTube Shorts technical requirements
- Composition completes within 2 minutes

#### US-2.3: Quality Validation
- **As a** quality control agent
- **I want** to validate video meets quality standards
- **So that** only high-quality content is published

**Acceptance Criteria:**
- Video duration is 15-60 seconds (±2 seconds tolerance)
- **Audio Levels**: 
  - Average loudness: -16 to -12 LUFS (Loudness Units relative to Full Scale)
  - Peak level: < -1 dBFS (no clipping)
  - Dynamic range: 6-12 dB
- **Video Resolution**: 1080x1920 minimum (9:16 aspect ratio)
- **Frame Rate**: 24fps minimum, 30fps preferred, 60fps maximum
- **File Size**: <100MB (for YouTube upload efficiency)
- **Sync Accuracy**: Audio-video sync error <200ms
- **Black Frame Detection**: No black frames >0.5 seconds
- **Policy Checks**: 
  - No prohibited keywords in title/description
  - No copyright-flagged content (basic keyword check)
  - Content rating appropriate (no explicit content)
- **Technical Glitches**: 
  - No frame drops >5% in any 1-second window
  - No audio dropouts >100ms
  - No visual artifacts (compression errors, pixelation)
- Validation completes within 30 seconds
- **Output**: Pass/Fail with detailed report of failures

### Epic 3: Publishing

#### US-3.1: YouTube Upload
- **As a** publishing agent
- **I want** to upload video to YouTube with metadata
- **So that** the content is published and discoverable

**Acceptance Criteria:**
- Video uploads successfully to YouTube
- Title, description, and tags are populated
- Video is set to public or unlisted (configurable)
- Upload completes within 5 minutes
- Upload status is logged

#### US-3.2: Execution Trigger
- **As a** system operator
- **I want** to manually trigger the generation pipeline
- **So that** I can test and control when videos are created

**Acceptance Criteria:**
- Pipeline can be triggered via CLI or API endpoint
- Execution provides progress feedback
- Errors are clearly reported
- Execution can be cancelled mid-process

### Epic 4: Error Handling & Observability

#### US-4.1: Error Logging
- **As a** system operator
- **I want** comprehensive error logging
- **So that** I can debug issues and monitor system health

**Acceptance Criteria:**
- All errors are logged with context
- Logs include timestamps and agent identification
- Critical errors trigger alerts
- Logs are searchable and structured

#### US-4.2: Pipeline Status
- **As a** system operator
- **I want** to see pipeline execution status
- **So that** I know if generation is in progress or completed

**Acceptance Criteria:**
- Status endpoint or CLI command shows current state
- Status includes current step and progress percentage
- Status shows last execution time and result
- Status includes any active errors

### Epic 5: Setup & Configuration

#### US-5.1: YouTube Authentication Setup
- **As a** system operator
- **I want** to authenticate with YouTube API
- **So that** videos can be uploaded automatically

**Acceptance Criteria:**
- OAuth 2.0 flow for YouTube API authentication
- Store access token and refresh token securely (environment variables or encrypted config)
- Automatic token refresh when expired
- Verify channel access and permissions before execution
- Clear error messages if authentication fails
- One-time setup process (documented in README)
- **Security**: Never expose tokens in logs or error messages

#### US-5.2: Configuration Management
- **As a** system operator
- **I want** to manage API keys and settings
- **So that** the system can access external services

**Acceptance Criteria:**
- **API Keys**: Store in `.env` file (environment variables)
  - OpenAI API key
  - ElevenLabs API key
  - RunwayML API key
  - YouTube OAuth credentials
  - Other service API keys
- **Settings**: Store in `config.yaml` or `config.json`
  - Timeouts, retry counts
  - Quality thresholds
  - Cost limits
  - Content preferences
- **Validation**: Validate all required keys and settings on startup
  - Check API keys are present and non-empty
  - Validate settings are within acceptable ranges
  - Provide clear error messages for missing/invalid config
- **Security**: `.env` file in `.gitignore` (never commit secrets)
- **Documentation**: Template `.env.example` file with all required keys

#### US-5.3: Partial Failure Recovery
- **As a** system
- **I want** to recover from partial failures
- **So that** work isn't lost and execution can resume

**Acceptance Criteria:**
- **Progress Tracking**: Save progress at each pipeline stage
  - Stage 1: Content research completed → Save topic and research data
  - Stage 2: Script generated → Save script text
  - Stage 3: Voice synthesis completed → Save audio file
  - Stage 4: Video assets generated → Save video files
  - Stage 5: Video composed → Save final video file
  - Stage 6: Quality validated → Save validation results
  - Stage 7: Uploaded to YouTube → Save YouTube video ID
- **Resume Capability**: 
  - If execution fails, detect last completed stage
  - Allow resume from last successful stage (optional feature for MVP)
  - Or restart from beginning with same topic (MVP default)
- **Failure Scenarios**:
  - **Video generated but upload fails**: Save video file, retry upload only
  - **Script generated but TTS fails**: Regenerate TTS only (reuse script)
  - **Pipeline timeout**: Save all completed work, log timeout, fail gracefully
  - **API quota exceeded**: Save progress, log error, wait for quota reset
- **Cleanup**: On successful completion, clean up temporary files
- **On Failure**: Keep temporary files for debugging (with expiration, e.g., 7 days)

#### US-5.4: Data Persistence
- **As a** system
- **I want** to persist execution data
- **So that** I can track history, costs, and content uniqueness

**Acceptance Criteria:**
- **Database**: SQLite database (local file: `youtube_shorts.db`)
- **Tables**:
  - **executions**: Execution history (id, status, start_time, end_time, error_message, cost_total)
  - **costs**: Cost breakdown per execution (execution_id, component, cost, timestamp)
  - **videos**: Video metadata (execution_id, title, description, youtube_id, publish_date, script_text)
  - **embeddings**: Content embeddings for uniqueness checking (video_id, embedding_vector, created_at)
  - **queue**: Queue state if using persistent queue (id, status, priority, created_at)
- **Data Retention**: 
  - Keep all execution history (no automatic deletion)
  - Keep embeddings for last 50 videos (for uniqueness checking)
  - Optional: Archive old data to JSON export
- **Queries**:
  - Get last N executions
  - Get cost history (total, by component, by date)
  - Get video metadata by YouTube ID
  - Get embeddings for similarity checking
- **Backup**: Optional export to JSON for backup/analysis
- **Performance**: Indexes on frequently queried fields (execution_id, youtube_id, created_at)

---

## Performance Requirements

**End-to-End Performance**
- **Target**: <10 minutes total pipeline execution
- **Component Timeouts**:
  - RAG Research: 30 seconds
  - Script Generation: 60 seconds
  - Voice Synthesis: 90 seconds
  - Video Asset Generation: 5 minutes
  - Video Composition: 2 minutes
  - Quality Validation: 30 seconds
  - YouTube Upload: 5 minutes
- **Total Buffer**: 1 minute for overhead

**Concurrency Handling**
- **MVP**: Single execution at a time (no concurrent runs)
- **Phase 2**: Support 2-3 concurrent executions (with resource limits)
- **Resource Limits per Execution**:
  - CPU: 2 cores maximum
  - Memory: 6-8GB maximum (video processing requires more RAM)
  - Disk: 5GB temporary storage (video files are large, 100MB+ per video)
  - Network: 10Mbps minimum bandwidth

**System Requirements (Local Development):**
- **Minimum RAM**: 8GB system RAM (for video processing)
- **Minimum Disk**: 10GB free space (for temporary files and database)
- **CPU**: 2+ cores recommended
- **Network**: 5Mbps upload for YouTube (minimum)
- **Note**: Ensure adequate system resources before execution

**Queue Management**
- **MVP**: Simple queue (FIFO) with manual trigger
- **Phase 2**: Priority queue (retry failed videos first)
- **Queue Limits**: Maximum 10 pending executions
- **Queue Persistence**: Store queue state (survive restarts)

**API Rate Limit Handling**
- **Detection**: Monitor API response codes (429, 503)
- **Backoff Strategy**: Exponential backoff (1s, 2s, 4s, 8s, 16s)
- **Rate Limit Tracking**: Track API usage per provider
- **Quota Alerts**: Warn when approaching 80% of quota

**Timeout Specifications**
- **Network Timeouts**: 30 seconds per API call
- **Processing Timeouts**: Component-specific (see above)
- **Total Pipeline Timeout**: 15 minutes (fail if exceeded)
- **Graceful Timeout**: Save partial progress, allow resume

**Resource Limits**
- **Disk Space**: Minimum 10GB free for temporary files
- **Memory**: Minimum 8GB system RAM
- **CPU**: Minimum 2 cores for video processing
- **Network**: Minimum 5Mbps upload for YouTube

---

## Configuration Management Approach

**Overview**: Centralized configuration management for API keys and system settings.

**API Keys Management:**
- **Storage**: `.env` file (environment variables)
- **Required Keys**:
  - `OPENAI_API_KEY`
  - `ELEVENLABS_API_KEY`
  - `RUNWAYML_API_KEY`
  - `YOUTUBE_CLIENT_ID`
  - `YOUTUBE_CLIENT_SECRET`
  - `YOUTUBE_REFRESH_TOKEN`
  - Other service API keys as needed
- **Security**: 
  - `.env` in `.gitignore`
  - Never log or expose keys in error messages
  - Use `python-dotenv` library to load variables

**Settings Management:**
- **Storage**: `config.yaml` or `config.json`
- **Settings Include**:
  - Timeouts (per component)
  - Retry counts and backoff strategies
  - Quality thresholds (coherence, similarity, etc.)
  - Cost limits and alert thresholds
  - Content preferences (topics, style, etc.)
  - Resource limits (memory, disk, etc.)
- **Validation**: Validate settings on startup (ranges, required fields)

**Implementation:**
- Load `.env` on startup
- Load `config.yaml` on startup
- Validate all required keys and settings
- Provide clear error messages for missing/invalid config
- Template files: `.env.example` and `config.example.yaml`

---

# Part 2: Technology Decisions (Reference - Read Only)

*Technology stack decisions. Update only if technology choices change.*

## Decision Matrices

### Decision Matrix 1: MCP Framework Approach

| Option | Pros | Cons | Cost | Complexity | Recommendation |
|--------|------|------|------|------------|----------------|
| **Custom MCP Framework** | Full control, optimized for use case, no dependencies | High development time, maintenance burden, testing overhead | $0 (dev time) | High | ❌ Not for MVP |
| **Existing MCP Library** | Proven framework, community support, faster development | Less customization, dependency on library updates | $0 (open source) | Medium | ✅ **Recommended for MVP** |
| **Simple Agent Orchestration** | Minimal dependencies, easy to understand, quick to build | Less structure, manual coordination, harder to scale | $0 | Low | ✅ **Alternative for MVP** |

**Recommendation**: **Simple Agent Orchestration** for MVP (Python with asyncio, SQLite for queue persistence if needed, or in-memory queue). Move to Redis/RabbitMQ in Phase 2 when concurrent execution is needed.

### Decision Matrix 2: Video Generation Solution

| Option | Pros | Cons | Cost per Video | Quality | Latency | Recommendation |
|--------|------|------|----------------|---------|---------|----------------|
| **RunwayML API** | High quality, realistic, good API | Expensive, rate limits | $0.05/sec (~$0.75-3.00/video for 15-60s) | ⭐⭐⭐⭐⭐ | 2-5 min | ✅ **Recommended for MVP** |
| **Pika Labs API** | Good quality, creative styles | Newer, less proven, rate limits | $0.05-0.08/sec (~$0.75-4.80/video for 15-60s) | ⭐⭐⭐⭐ | 3-6 min | ✅ Alternative |
| **Stock Footage + AI Composition** | Reliable, predictable, lower cost | Less unique, requires library access | $0.50-1.50/video | ⭐⭐⭐ | 1-2 min | ✅ **Fallback option** |

**Recommendation**: **RunwayML API** for MVP (best quality/cost balance, ~$0.75-3.00 per video for 15-60 seconds). **Stock Footage + AI Composition** as fallback (reliable, cost-effective, ~$0.50-1.50 per video).

### Decision Matrix 3: Text-to-Speech (TTS) Solution

| Option | Pros | Cons | Cost per Video | Quality | Latency | Recommendation |
|--------|------|------|----------------|---------|---------|----------------|
| **ElevenLabs** | Best quality, natural, multiple voices | Expensive, rate limits | $0.18-0.30/min (~$0.30-0.90/video) | ⭐⭐⭐⭐⭐ | 10-30 sec | ✅ **Recommended for MVP** |
| **Google Cloud TTS** | Reliable, good quality, scalable | Less natural than ElevenLabs | $0.016/min (~$0.02-0.05/video) | ⭐⭐⭐⭐ | 5-15 sec | ✅ **Cost-effective alternative** |

**Recommendation**: **ElevenLabs** for MVP (best quality, acceptable cost). **Google Cloud TTS** as cost-optimization option in Phase 2.

### Decision Matrix 4: RAG System Architecture

| Option | Pros | Cons | Cost per Month | Setup Complexity | Recommendation |
|--------|------|------|----------------|------------------|----------------|
| **Pinecone** | Managed, scalable, easy API | Expensive at scale | $70-200/month | Low | ✅ **Phase 2 option** |
| **ChromaDB (Local)** | Free, simple, good for MVP | Requires hosting, no managed scaling | $0 | Medium | ✅ **Cost-effective MVP option** |

**Recommendation**: **ChromaDB (Local)** for MVP (free, sufficient for MVP scale). **Pinecone** for Phase 2 (when scaling beyond 1000 videos).

### Decision Matrix 5: LLM for Content Generation

| Option | Pros | Cons | Cost per Video | Quality | Latency | Recommendation |
|--------|------|------|----------------|---------|---------|----------------|
| **OpenAI GPT-4** | Best quality, creative, reliable | Expensive | $0.03-0.10/1K tokens (~$0.20-0.50/video) | ⭐⭐⭐⭐⭐ | 5-15 sec | ✅ **Recommended for MVP** |
| **OpenAI GPT-3.5 Turbo** | Good quality, cost-effective | Less creative than GPT-4 | $0.0015-0.002/1K tokens (~$0.02-0.05/video) | ⭐⭐⭐⭐ | 3-10 sec | ✅ **Cost-optimization option** |

**Recommendation**: **GPT-4** for script generation (MVP quality). **GPT-3.5 Turbo** for metadata and summaries (cost optimization).

### Decision Matrix 6: Deployment Strategy

| Option | Pros | Cons | Cost per Month | Complexity | Recommendation |
|--------|------|------|----------------|------------|----------------|
| **Local Development** | Free, full control, easy debugging, no setup | Manual execution, not production-ready | $0 | Low | ✅ **MVP ONLY** |
| **Docker + Cron (VPS)** | Simple, reliable, full control | Manual scaling, server management | $5-20/month (VPS) | Low | ✅ **Phase 2 option** |
| **Google Cloud Run** | Serverless, good for containers, scalable | Cold starts, cost at scale | $10-30/month | Medium | ✅ **Phase 2 option** |

**Recommendation by Phase:**
- **MVP**: **Local Development Only** (runs on developer's machine, manual execution via CLI or Python script)
- **Phase 2**: **Docker + Cron on VPS** OR **Google Cloud Run** (when automation needed)

### Decision Matrix 7: Content Strategy

| Option | Pros | Cons | Engagement Potential | Competition Level | Recommendation |
|--------|------|------|---------------------|-------------------|----------------|
| **Trending Topics (General)** | High discoverability, broad appeal | High competition, fast-changing | ⭐⭐⭐⭐ | High | ✅ **Recommended for MVP** |
| **Educational Content** | Evergreen, high value, good retention | Requires accuracy, research time | ⭐⭐⭐⭐ | Medium | ✅ **Phase 2 option** |

**Recommendation**: **Trending Topics (General)** for MVP with **Educational Content** as secondary (70/30 mix).

### Decision Matrix 8: Data Storage Solution

| Option | Pros | Cons | Cost | Complexity | What to Store | Recommendation |
|--------|------|------|------|------------|---------------|----------------|
| **SQLite** | Free, no setup, file-based, ACID transactions | Not for high concurrency, file size limits | $0 | Low | All MVP data | ✅ **Recommended for MVP** |
| **PostgreSQL** | Robust, scalable, full SQL, production-ready | Requires setup, database server, overkill for MVP | $0 (local) or $10-50/month (managed) | Medium | All data | ✅ **Phase 2 option** |

**Recommendation**: **SQLite** for MVP (local file `youtube_shorts.db`, no setup required, sufficient for MVP scale). **PostgreSQL** for Phase 2 (when scaling beyond local development or need concurrent access).

### Decision Matrix 9: Code Quality Framework

| Option | Pros | Cons | Cost | Complexity | Recommendation |
|--------|------|------|------|------------|----------------|
| **Claude Pilot** | Automated quality, TDD enforcement, spec-driven, Python support | Commercial license, learning curve | License fee | Low-Medium | ✅ **Recommended** |
| **Manual Quality** | Free, full control | Time-consuming, inconsistent, no enforcement | $0 | High | ❌ Not scalable |
| **Basic Hooks Only** | Free, some automation | Limited features, no TDD enforcement | $0 | Medium | ⚠️ Alternative |

**Decision Criteria:**
- **Quality Priority**: Claude Pilot (automated, enforced)
- **Cost Priority**: Basic hooks (but less effective)
- **Speed Priority**: Claude Pilot (saves time on quality checks)

**Recommendation**: **Claude Pilot** for MVP (ensures production-quality code, reduces bugs, speeds development)

---

## Final MVP Technology Stack

**Core Framework:**
- **Orchestration**: Python asyncio + SQLite (for queue persistence if needed, or in-memory queue)
- **Language**: Python 3.11+
- **Data Storage**: SQLite database (`youtube_shorts.db`)

**Content Generation:**
- **LLM**: OpenAI GPT-4 (script generation), GPT-3.5 Turbo (metadata)
- **RAG**: ChromaDB (local) with OpenAI embeddings
- **TTS**: ElevenLabs API

**Video Production:**
- **Video Generation**: RunwayML API (primary), Stock Footage + AI Composition (fallback)
- **Video Processing**: FFmpeg (local)
- **Composition**: MoviePy or FFmpeg Python bindings

**Publishing:**
- **YouTube API**: Google YouTube Data API v3

**Infrastructure:**
- **Deployment**: **Local Development Only** (runs on developer's machine, manual execution)
- **Storage**: 
  - Local filesystem (temporary video files)
  - SQLite database (execution history, costs, metadata, embeddings)
- **Configuration**: `.env` file (API keys) + `config.yaml` (settings)
- **Monitoring**: Structured logging (JSON) + health check command

**Development Tools:**
- **Code Quality Framework**: Claude Pilot (auto-formatting, linting, type-checking, TDD enforcement)
- **Installation**: Run `curl -fsSL https://raw.githubusercontent.com/maxritter/claude-pilot/main/install.sh | bash` in project directory
- **Purpose**: Automated code quality, testing enforcement, spec-driven development
- **Integration**: Works alongside PROJECT_WORKSPACE.md (Pilot = code quality, Workspace = agent coordination)

**Estimated MVP Monthly Cost (30 videos):**
- **Infrastructure**: $0 (local development, no VPS or cloud services)
- **API Costs**:
  - **RAG/Research**: $3 (ChromaDB free, embeddings ~$0.10/video)
  - **LLM Content Generation**: $15 (GPT-4 for scripts ~$0.40/video, GPT-3.5 for metadata ~$0.10/video)
  - **TTS/Voice Synthesis**: $27 (ElevenLabs ~$0.90/video for 30-60s videos)
  - **Video Generation**: $60-90 (RunwayML ~$2-3/video for 15-60s videos, using average $2.50/video)
  - **Storage & Processing**: $0 (local filesystem, FFmpeg free)
  - **YouTube API**: $0 (free quota sufficient)
  - **Other APIs**: $3 (embeddings, rate limits)
- **Subtotal**: ~$108-138/month
- **20% Buffer**: ~$22-28/month (for unexpected costs, retries, longer videos)
- **Total**: ~$130-166/month (~$4.33-5.53 per video)
- **Target**: <$5.00 per video (within budget with buffer)

**MVP Execution Model:**
- **Environment**: Developer's local machine (macOS, Linux, or Windows)
- **Trigger**: Manual execution via CLI command or Python script
- **Requirements**: 8GB RAM, 10GB free disk space, Python 3.11+, FFmpeg installed
- **Setup**: Install dependencies, configure `.env` with API keys, run health check
- **Execution**: Single video generation per run, no concurrent executions
- **Output**: Video published to YouTube, execution logged to SQLite database

---

# Part 3: Active Development (Collaborative - All Updates Here)

*Active development work documented here. All agents update this section.*

## System Architecture

**Status**: ✅ Design Complete | 🔄 Pending CTO Approval  
**Designed By**: Architect  
**Date**: 2024-01-15 17:00 UTC  
**Approval Request**: Approval #001 (see Approval Requests section)

---

### Architecture Overview

The system uses a **Simple Agent Orchestration** pattern with Python asyncio for concurrent agent coordination. Each agent is a specialized component handling one stage of the video generation pipeline. Agents communicate via a message queue (SQLite-based for MVP) and share state through a centralized database.

**Key Principles:**
- **Single Responsibility**: Each agent handles one pipeline stage
- **Async Communication**: Non-blocking message passing between agents
- **State Persistence**: All progress saved to SQLite at each stage
- **Error Recovery**: Graceful failure handling with partial progress preservation
- **Cost Tracking**: Real-time cost logging per component

---

### Framework Structure

```
youtube-shorts-generator/
├── src/
│   ├── agents/              # Agent implementations
│   │   ├── __init__.py
│   │   ├── base_agent.py    # Base agent class
│   │   ├── research_agent.py
│   │   ├── script_agent.py
│   │   ├── tts_agent.py
│   │   ├── video_agent.py
│   │   ├── composition_agent.py
│   │   ├── quality_agent.py
│   │   └── publishing_agent.py
│   ├── orchestration/       # Pipeline orchestration
│   │   ├── __init__.py
│   │   ├── pipeline.py      # Main pipeline orchestrator
│   │   ├── message_queue.py # SQLite-based message queue
│   │   └── state_manager.py # Execution state management
│   ├── services/            # External service integrations
│   │   ├── __init__.py
│   │   ├── openai_service.py
│   │   ├── elevenlabs_service.py
│   │   ├── runwayml_service.py
│   │   ├── youtube_service.py
│   │   └── rag_service.py
│   ├── database/            # Database layer
│   │   ├── __init__.py
│   │   ├── models.py        # SQLAlchemy models
│   │   ├── repository.py    # Data access layer
│   │   └── migrations.py   # Schema migrations
│   ├── utils/              # Shared utilities
│   │   ├── __init__.py
│   │   ├── logging.py      # Structured logging
│   │   ├── cost_tracker.py # Cost tracking utilities
│   │   └── config.py      # Configuration management
│   └── cli/                # CLI interface
│       ├── __init__.py
│       └── main.py         # Entry point
├── tests/                  # Test suite
├── config.yaml            # System settings
├── .env                   # API keys (gitignored)
├── youtube_shorts.db      # SQLite database
└── README.md
```

---

### Agent Architecture

#### Base Agent Interface

All agents inherit from `BaseAgent` which provides:
- **Message Handling**: Receive and send messages via queue
- **State Management**: Save/load execution state
- **Cost Tracking**: Log API costs automatically
- **Error Handling**: Standardized retry logic and error reporting
- **Progress Reporting**: Update pipeline status

```python
class BaseAgent(ABC):
    """Base class for all pipeline agents"""
    
    async def execute(self, context: ExecutionContext) -> AgentResult:
        """Execute agent's primary task"""
        pass
    
    async def handle_message(self, message: Message) -> None:
        """Process incoming messages"""
        pass
    
    def save_progress(self, stage: str, data: dict) -> None:
        """Save progress to database"""
        pass
    
    def log_cost(self, component: str, cost: float) -> None:
        """Log API cost"""
        pass
```

#### Agent Responsibilities

**1. ResearchAgent** (US-1.1)
- **Input**: None (triggers pipeline)
- **Output**: Topic, title suggestions, key points, relevance scores
- **Services**: RAG (ChromaDB), OpenAI embeddings
- **Timeout**: 30 seconds
- **Cost Target**: <$0.10

**2. ScriptAgent** (US-1.2)
- **Input**: Research data (topic, key points)
- **Output**: 15-60 second script text
- **Services**: OpenAI GPT-4
- **Timeout**: 60 seconds
- **Cost Target**: <$0.40

**3. UniquenessAgent** (US-1.4)
- **Input**: Generated script
- **Output**: Similarity scores, pass/fail decision
- **Services**: OpenAI embeddings, SQLite (previous videos)
- **Timeout**: 10 seconds
- **Cost Target**: <$0.05

**4. TTSAgent** (US-1.3)
- **Input**: Script text
- **Output**: Audio file (WAV/MP3)
- **Services**: ElevenLabs API
- **Timeout**: 90 seconds
- **Cost Target**: <$0.90

**5. VideoAgent** (US-2.1)
- **Input**: Script text, scene breakdown
- **Output**: Video asset files (or fallback assets)
- **Services**: RunwayML API (primary), Stock footage (fallback)
- **Timeout**: 5 minutes
- **Cost Target**: <$2.50
- **Fallback Chain**: RunwayML → Stock → Animated → Static

**6. CompositionAgent** (US-2.2)
- **Input**: Audio file, video assets
- **Output**: Final composed video (MP4, 1080x1920)
- **Services**: FFmpeg (local), MoviePy
- **Timeout**: 2 minutes
- **Cost Target**: $0 (local processing)

**7. QualityAgent** (US-2.3)
- **Input**: Final video file
- **Output**: Validation report (pass/fail, detailed checks)
- **Services**: FFmpeg analysis (local)
- **Timeout**: 30 seconds
- **Cost Target**: $0 (local processing)
- **Checks**: Duration, resolution, audio levels, sync, policy

**8. PublishingAgent** (US-3.1)
- **Input**: Final video, metadata (title, description)
- **Output**: YouTube video ID, publish status
- **Services**: YouTube Data API v3
- **Timeout**: 5 minutes
- **Cost Target**: $0 (free quota)

---

### Data Flow

#### Pipeline Execution Flow

```
[CLI Trigger]
    ↓
[Pipeline Orchestrator]
    ↓
[ResearchAgent] → Topic + Research Data
    ↓ (save progress)
[ScriptAgent] → Script Text
    ↓ (save progress)
[UniquenessAgent] → Similarity Check
    ↓ (if pass)
[TTSAgent] → Audio File
    ↓ (save progress)
[VideoAgent] → Video Assets
    ↓ (save progress)
[CompositionAgent] → Final Video
    ↓ (save progress)
[QualityAgent] → Validation Report
    ↓ (if pass)
[PublishingAgent] → YouTube Video ID
    ↓ (save progress)
[Complete] → Cleanup + Log
```

#### State Persistence Flow

Each agent saves progress to SQLite:
1. **Before Execution**: Load previous state (if resuming)
2. **During Execution**: Save intermediate results
3. **After Execution**: Save final output + metadata
4. **On Failure**: Save error + partial results for recovery

#### Message Queue Flow

Agents communicate via SQLite-based message queue:
- **Producer**: Agent sends message to queue (next stage)
- **Consumer**: Next agent polls queue for messages
- **Acknowledgment**: Message removed after successful processing
- **Retry**: Failed messages retried with exponential backoff

---

### Communication Patterns

#### 1. Synchronous Pipeline (MVP)
- Agents execute sequentially
- Each agent waits for previous agent to complete
- State passed via ExecutionContext object
- No concurrent agent execution

#### 2. Message Queue Pattern
- SQLite table: `message_queue`
- Columns: `id`, `from_agent`, `to_agent`, `message_type`, `payload`, `status`, `created_at`
- Status: `pending`, `processing`, `completed`, `failed`

#### 3. State Sharing Pattern
- Centralized ExecutionContext object
- Passed between agents
- Persisted to database at each stage
- Loaded on resume

#### 4. Error Propagation Pattern
- Errors wrapped in AgentResult object
- Contains: success flag, error message, partial data
- Propagated to orchestrator
- Orchestrator decides: retry, fallback, or fail

---

### Component Interactions

#### Orchestrator → Agents
- Creates ExecutionContext
- Invokes agents in sequence
- Handles errors and retries
- Tracks overall progress

#### Agents → Services
- Agents call service classes (not direct API calls)
- Services handle: API calls, retries, rate limiting, cost tracking
- Services return standardized results

#### Agents → Database
- Via Repository pattern
- Repository handles: SQL queries, transactions, error handling
- Agents don't write SQL directly

#### Agents → Message Queue
- Via MessageQueue class
- Handles: enqueue, dequeue, acknowledgment, retry logic

---

### Database Schema

**executions** table:
- `id` (INTEGER PRIMARY KEY)
- `status` (TEXT: pending, in_progress, completed, failed)
- `start_time` (TIMESTAMP)
- `end_time` (TIMESTAMP)
- `current_stage` (TEXT)
- `error_message` (TEXT)
- `cost_total` (REAL)

**costs** table:
- `id` (INTEGER PRIMARY KEY)
- `execution_id` (INTEGER, FK)
- `component` (TEXT: research, script, tts, video, etc.)
- `cost` (REAL)
- `timestamp` (TIMESTAMP)

**videos** table:
- `id` (INTEGER PRIMARY KEY)
- `execution_id` (INTEGER, FK)
- `title` (TEXT)
- `description` (TEXT)
- `youtube_id` (TEXT)
- `publish_date` (TIMESTAMP)
- `script_text` (TEXT)

**embeddings** table:
- `id` (INTEGER PRIMARY KEY)
- `video_id` (INTEGER, FK)
- `embedding_vector` (BLOB)  # Stored as JSON array
- `created_at` (TIMESTAMP)

**message_queue** table:
- `id` (INTEGER PRIMARY KEY)
- `from_agent` (TEXT)
- `to_agent` (TEXT)
- `message_type` (TEXT)
- `payload` (TEXT)  # JSON string
- `status` (TEXT)
- `created_at` (TIMESTAMP)
- `processed_at` (TIMESTAMP)

---

### Error Handling & Recovery

#### Retry Strategy
- **API Calls**: 3 retries with exponential backoff (1s, 2s, 4s)
- **Transient Failures**: Automatic retry (network errors, rate limits)
- **Permanent Failures**: Log and fail gracefully

#### Partial Failure Recovery
- **Progress Saved**: At each stage completion
- **Resume Capability**: Detect last completed stage from database
- **MVP Default**: Restart from beginning (resume optional for Phase 2)
- **Failure Scenarios**:
  - Video generated but upload fails → Retry upload only
  - Script generated but TTS fails → Regenerate TTS only
  - Pipeline timeout → Save all work, log timeout

#### Error Propagation
- Agent errors wrapped in `AgentResult`
- Orchestrator handles: retry, fallback, or fail
- All errors logged with context
- Critical errors trigger alerts

---

### Cost Tracking

#### Real-Time Cost Logging
- Each service call logs cost immediately
- Cost stored in `costs` table with component name
- Total cost calculated per execution
- Cost alerts triggered at thresholds

#### Cost Components
- Research: RAG queries + embeddings
- Script: GPT-4 API calls
- TTS: ElevenLabs API calls
- Video: RunwayML API calls
- Other: YouTube API, other services

---

### Configuration Management

#### Environment Variables (.env)
- `OPENAI_API_KEY`
- `ELEVENLABS_API_KEY`
- `RUNWAYML_API_KEY`
- `YOUTUBE_CLIENT_ID`
- `YOUTUBE_CLIENT_SECRET`
- `YOUTUBE_REFRESH_TOKEN`

#### Settings File (config.yaml)
- Timeouts per component
- Retry counts and backoff strategies
- Quality thresholds
- Cost limits and alert thresholds
- Content preferences
- Resource limits

---

### Development Quality Layer

Claude Pilot provides automated code quality enforcement:
- Runs hooks on every file edit (formatting, linting, type-checking)
- Enforces TDD (tests required before completion)
- Complements MCP framework (Pilot = code quality, MCP = agent communication)

---

### Architecture Decisions

1. **Simple Agent Orchestration**: Chosen over full MCP library for MVP simplicity
2. **SQLite Message Queue**: File-based, no setup, sufficient for single execution
3. **Sequential Execution**: MVP supports single execution at a time
4. **State Persistence**: SQLite database for all state (executions, costs, videos)
5. **Service Layer**: Abstraction over external APIs for testability
6. **Repository Pattern**: Database access abstraction
7. **Async/Await**: Python asyncio for non-blocking I/O

---

### Future Enhancements (Phase 2+)

- **Concurrent Execution**: Support 2-3 parallel executions
- **Redis Queue**: Replace SQLite queue for better concurrency
- **Resume Capability**: Full resume from any stage
- **Advanced Retry**: Circuit breakers, fallback providers
- **Monitoring Dashboard**: Real-time pipeline status
- **Multi-Agent Coordination**: Agents can communicate directly (not just via queue)

---

**Architecture Status**: ✅ Design Complete | ✅ Approved by CTO (Approval #001)  
**Next Step**: Implementation Planning → Implementation (Lead Engineer)

---

## Implementation Plan

**Status**: 🟡 In Progress - Architecture Approved  
**Created By**: Lead Engineer  
**Date**: 2026-02-14 21:30 UTC  
**Based On**: Approved Architecture (Approval #001)

---

### Implementation Phases

#### Phase 1: Project Setup & Foundation (Week 1)
**Goal**: Establish project structure, development environment, and core infrastructure

**Tasks:**
1. **Project Structure Setup**
   - [x] Create directory structure per architecture (src/agents, src/orchestration, src/services, etc.) - ✅ 2026-02-14 21:37
   - [x] Initialize Python package structure with `__init__.py` files - ✅ 2026-02-14 21:37
   - [x] Set up `.gitignore` (exclude .env, __pycache__, *.db, etc.) - ✅ 2026-02-14 21:37
   - [x] Create initial `README.md` with setup instructions - ✅ 2026-02-14 21:37

2. **Development Environment**
   - [x] Set up Python 3.11+ virtual environment (✅ 2026-02-14 23:55)
   - [x] Install core dependencies (asyncio, SQLite, PyYAML, python-dotenv) (✅ 2026-02-14 23:55)
   - [ ] Install Claude Pilot: `curl -fsSL https://raw.githubusercontent.com/maxritter/claude-pilot/main/install.sh | bash`
   - [ ] Run `/sync` to generate project-specific Pilot rules
   - [ ] Create custom Pilot rules:
     - `.claude/rules/agent-guidelines.mdc` - References PROJECT_WORKSPACE.md
     - `.claude/rules/content-generation.mdc` - Content generation standards
     - `.claude/rules/video-quality.mdc` - Video processing standards
     - `.claude/rules/mcp-framework.mdc` - Agent communication standards
   - [ ] Test Pilot integration (formatting, linting, type-checking)

3. **Configuration Management**
   - [x] Create `config.yaml` template with all settings (timeouts, retry counts, thresholds) (✅ 2026-02-14 24:25 - config.example.yaml)
   - [x] Create `.env.example` with all required API keys (no actual keys) (✅ 2026-02-14 24:25)
   - [x] Implement `src/utils/config.py` to load and validate configuration (✅ 2026-02-14 24:25)
   - [ ] Add configuration validation on startup (call get_config in CLI when implemented)

4. **Database Setup**
   - [x] Design SQLite schema (executions, costs, videos, embeddings, message_queue tables) (✅ 2026-02-14 24:35)
   - [x] Implement `src/database/models.py` (dataclasses + constants) (✅ 2026-02-14 24:35)
   - [x] Implement `src/database/repository.py` for data access (✅ 2026-02-14 24:35)
   - [x] Create `src/database/migrations.py` for schema initialization (✅ 2026-02-14 24:35)
   - [x] Test database creation and migrations (✅ 2026-02-14 24:35)

5. **Logging & Utilities**
   - [x] Implement `src/utils/logging.py` with structured JSON logging (✅ 2026-02-14 24:38)
   - [x] Implement `src/utils/cost_tracker.py` for cost tracking (✅ 2026-02-14 24:38)
   - [ ] Set up log rotation and file management (optional Phase 1)

#### Phase 2: Core Infrastructure (Week 2)
**Goal**: Build orchestration, message queue, and state management

**Tasks:**
1. **Base Agent Framework**
   - [x] Implement `src/agents/base_agent.py` with BaseAgent abstract class (✅ 24:40)
   - [x] Implement message handling, state management, cost tracking (✅ in BaseAgent)
   - [ ] Implement error handling and retry logic (in agents)
   - [x] Add unit tests for BaseAgent (✅ tests/test_base_agent.py, 12 tests)

2. **Message Queue**
   - [x] Implement `src/orchestration/message_queue.py` with SQLite-based queue (✅ 24:45)
   - [x] Support: enqueue, dequeue, acknowledgment (✅)
   - [x] Add message status tracking (pending, processing, completed, failed) (✅)
   - [x] Test queue operations and concurrency handling (✅ tests/test_message_queue.py, 10 tests)

3. **State Management**
   - [x] Implement `src/orchestration/state_manager.py` for execution state (✅ 24:45)
   - [x] Support: save progress, load state (✅ create_execution, load_context, save_stage)
   - [ ] Resume capability (optional)
   - [x] Test state persistence and recovery (✅ tests/test_state_manager.py, 8 tests)

4. **Pipeline Orchestrator**
   - [x] Implement `src/orchestration/pipeline.py` as main orchestrator (✅ 24:45)
   - [x] Sequential agent execution (MVP) (✅)
   - [ ] Error handling and retry logic (basic; enhance in agents)
   - [ ] Progress tracking and reporting
   - [x] Test end-to-end orchestration flow (✅ tests/test_pipeline.py, 7 tests)

#### Phase 3: Service Layer (Week 3)
**Goal**: Implement external API integrations with retry logic and cost tracking

**Tasks:**
1. **OpenAI Service**
   - [x] Implement `src/services/openai_service.py` (✅ 25:00)
   - [x] GPT-4 chat, embeddings, cost, retry

2. **RAG Service**
   - [x] Implement `src/services/rag_service.py` (✅ 25:00)
   - [x] ChromaDB, similarity_search, query_topics

3. **ElevenLabs Service**
   - [x] Implement `src/services/elevenlabs_service.py` (✅ 25:00)
   - [x] text_to_speech, cost estimate

4. **RunwayML Service**
   - [x] Implement `src/services/runwayml_service.py` (stub) (✅ 25:00)

5. **YouTube Service**
   - [x] Implement `src/services/youtube_service.py` (✅ 25:00)
   - [x] OAuth, upload_video

#### Phase 4: Agent Implementations (Week 4-5)
**Goal**: Implement all 8 pipeline agents

**Tasks:**
1. **ResearchAgent** (US-1.1) - [x] research_agent.py (✅ 25:00)
2. **ScriptAgent** (US-1.2) - [x] script_agent.py (✅ 25:00)
3. **UniquenessAgent** (US-1.4) - [x] uniqueness_agent.py (✅ 25:00)
4. **TTSAgent** (US-1.3) - [x] tts_agent.py (✅ 25:00)
5. **VideoAgent** (US-2.1) - [x] video_agent.py (stub) (✅ 25:00)
6. **CompositionAgent** (US-2.2) - [x] composition_agent.py (stub) (✅ 25:00)
7. **QualityAgent** (US-2.3) - [x] quality_agent.py (stub) (✅ 25:00)
8. **PublishingAgent** (US-3.1) - [x] publishing_agent.py (✅ 25:00)

#### Phase 5: CLI & Integration (Week 6)
**Goal**: Create CLI interface and integrate all components

**Tasks:**
1. **CLI Interface**
   - [x] Implement `src/cli/main.py` (✅ 25:00)
   - [x] Commands: generate, status, health

2. **Health Check**
   - [x] Implement health check command/endpoint (✅ src/utils/health.py, cmd_health())
   - [x] Check API connectivity (✅ openai, elevenlabs, runwayml, youtube_channel)
   - [x] Verify API key validity (✅ api_keys check)
   - [x] Check disk space (minimum 10GB) (✅ check_disk_space)
   - [x] Check system resources (8GB RAM, CPU cores) (✅ system_resources)
   - [x] Verify YouTube channel access (✅ youtube_channel)
   - [x] Check database connectivity (✅ database/SQLite)
   - [x] Return JSON status report (✅ run_all_checks)

3. **Error Recovery**
   - [ ] Implement partial failure recovery
   - [ ] Progress saving at each stage
   - [ ] Resume capability (optional for MVP, default: restart)
   - [ ] Cleanup of temporary files

4. **Testing**
   - [ ] Unit tests for all agents
   - [ ] Integration tests for pipeline
   - [ ] Service layer tests (with mocks)
   - [ ] End-to-end test with mock APIs

#### Phase 6: Documentation & Polish (Week 7)
**Goal**: Complete documentation and finalize MVP

**Tasks:**
1. **Documentation**
   - [ ] Complete README.md with setup instructions
   - [ ] API documentation for services
   - [ ] Agent documentation
   - [ ] Troubleshooting guide
   - [ ] Configuration reference

2. **Code Quality**
   - [ ] Run all tests and achieve >80% coverage
   - [ ] Code review and refactoring
   - [ ] Performance optimization
   - [ ] Error message improvements

3. **Final Testing**
   - [ ] End-to-end test with real APIs (test mode)
   - [ ] Cost tracking verification
   - [ ] Error handling validation
   - [ ] Performance testing (<10 minutes total)

---

### Dependencies

**Core Python Libraries:**
- `asyncio` (built-in) - Async agent coordination
- `sqlite3` (built-in) - Database
- `PyYAML>=6.0` - Configuration management
- `python-dotenv>=1.0.0` - Environment variable loading

**External APIs:**
- `openai>=1.0.0` - GPT-4, GPT-3.5, embeddings
- `chromadb>=0.4.0` - Local vector database
- `elevenlabs>=0.2.0` - Text-to-speech
- `google-api-python-client>=2.0.0` - YouTube API
- `google-auth-httplib2>=0.1.0` - YouTube OAuth
- `google-auth-oauthlib>=1.0.0` - YouTube OAuth

**Video Processing:**
- `moviepy>=1.0.3` - Video composition
- `ffmpeg-python>=0.2.0` - FFmpeg bindings (or subprocess calls)

**Utilities:**
- `pydantic>=2.0.0` - Data validation
- `structlog>=23.0.0` - Structured logging

**Development:**
- `pytest>=7.0.0` - Testing framework
- `pytest-asyncio>=0.21.0` - Async test support
- `pytest-mock>=3.10.0` - Mocking

---

### Development Environment Setup

**Pilot Installation & Configuration:**
- [x] Install Claude Pilot in project directory
- [ ] Run `/sync` to generate project-specific rules
- [ ] Create custom rules referencing PROJECT_WORKSPACE.md
- [ ] Configure Pilot hooks for Python code quality
- [ ] Test Pilot integration (formatting, linting, type-checking)
- [x] Document Pilot usage in README (✅ 2026-02-15)

**Custom Pilot Rules to Create:**
- `.claude/rules/agent-guidelines.mdc` - References PROJECT_WORKSPACE.md for agent coordination
- `.claude/rules/content-generation.mdc` - Standards for content generation code
- `.claude/rules/video-quality.mdc` - Standards for video processing code
- `.claude/rules/mcp-framework.mdc` - Standards for MCP agent communication

---

### Implementation Notes

**Code Organization:**
- Follow the approved architecture structure exactly
- Use async/await throughout for non-blocking I/O
- Implement Repository pattern for database access
- Service layer abstracts all external API calls

**Testing Strategy:**
- Unit tests for each agent (mock services)
- Integration tests for pipeline (mock APIs)
- End-to-end test with real APIs in test mode
- Target: >80% code coverage

**Cost Management:**
- Track costs at every API call
- Log to database immediately
- Alert if cost exceeds thresholds
- Monthly cost target: <$5.00 per video

**Error Handling:**
- Retry logic: 3 retries with exponential backoff
- Save progress at each stage
- Graceful failure with clear error messages
- Partial failure recovery (save work, allow resume)

**Performance Targets:**
- Total pipeline: <10 minutes
- Each agent within timeout limits
- Efficient database queries (indexes)
- Minimal memory footprint

---

### Next Steps

1. **Immediate**: Set up project structure and development environment
2. **Week 1**: Complete Phase 1 (Project Setup & Foundation)
3. **Week 2**: Complete Phase 2 (Core Infrastructure)
4. **Continue**: Follow phased approach through Week 7

**Blockers**: None - Architecture approved, ready to start implementation

---

## Development Progress

*[All agents log progress here]*

**Status**: ⏳ Not Started - Waiting for implementation plan

**Planned Sections:**
- What's built
- What's working
- What's next
- Issues encountered

### Development Workflow with Pilot

**Two-Layer System:**
1. **Agent Coordination Layer** (PROJECT_WORKSPACE.md)
   - Architect designs → Requests CTO approval → Logs in workspace
   - Lead Engineer implements → Logs progress in workspace
   - All approvals and coordination via workspace

2. **Code Quality Layer** (Claude Pilot)
   - Lead Engineer writes code → Pilot auto-formats/lints
   - TDD enforcement → Tests required before completion
   - Type checking → Catches errors automatically
   - Spec-driven development → `/spec` for complex features

**Integration Points:**
- Workspace tracks WHAT needs to be built (tasks, approvals)
- Pilot ensures HOW it's built (quality, testing, standards)
- Both systems work in parallel, complementary roles

---

## Testing Strategy

*[Lead Engineer/Junior Engineer documents here]*

**Status**: ⏳ Not Started - Waiting for implementation

---

## Documentation

*[Junior Engineer/PM maintains here]*

**Status**: ⏳ Not Started - Waiting for code

**Planned:**
- README.md
- API documentation
- Setup guides
- Troubleshooting

---

**Document End** - All agents continue collaboration below this line.


<!-- Test comment added for monitoring test -->
