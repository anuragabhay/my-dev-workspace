"""
Orchestrator brain: two-model propose → critique → synthesize flow using A2A.

Proposer (Model A): Receives context (MCP results, PROJECT_WORKSPACE), produces
initial proposal. Critic (Model B): Receives proposal, critiques it. Synthesizer
(Model A): Receives critique, produces final decision. All handoffs use A2A
message format for consistency and future extensibility.
"""

import json
import uuid
from typing import Any, Optional

from orchestrator_client.a2a import (
    A2AMessage,
    create_proposal,
    create_critique,
    create_synthesis,
)
from orchestrator_client.config import (
    get_anthropic_api_key,
    get_proposer_model,
    get_critic_model,
)


def _call_llm(
    model: str, system: str, user: str, api_key_override: Optional[str] = None
) -> str:
    """Call Anthropic API with system and user messages."""
    api_key = api_key_override or get_anthropic_api_key()
    if not api_key:
        raise RuntimeError(
            "ANTHROPIC_API_KEY or ORCHESTRATOR_LLM_API_KEY not set. "
            "Set one of these env vars to run the orchestrator brain."
        )

    from anthropic import Anthropic

    client = Anthropic(api_key=api_key)
    response = client.messages.create(
        model=model,
        max_tokens=2048,
        system=system,
        messages=[{"role": "user", "content": user}],
    )

    if not response.content:
        return ""
    parts = []
    for block in response.content:
        if hasattr(block, "text"):
            parts.append(block.text)
    return "\n".join(parts)


def _proposer_prompt(context: dict[str, Any]) -> str:
    """Build the user prompt for the Proposer (Phase 1)."""
    return f"""Run one orchestrator cycle.

## MCP Tool Results

### get_pending_orchestrator_prompt
```json
{json.dumps(context.get("pending_prompt", {}), indent=2)}
```

### get_workspace_status
```json
{json.dumps(context.get("workspace_status", {}), indent=2)}
```

### get_workflow_config
```json
{json.dumps(context.get("workflow_config", {}), indent=2)}
```

## PROJECT_WORKSPACE.md (snippet)
```
{context.get("workspace_snippet", "(not provided)")}
```

---

Apply the workflow and decision rules from the system context. Propose the single next action. Output exactly one of:
1. A delegation: `/role task` (e.g. `/lead-engineer Add unit tests for health.py`)
2. User Intervention Required: [reason]
3. ORCHESTRATION_COMPLETE: [brief summary]
4. Run one cycle: get_workspace_status, read PROJECT_WORKSPACE.md, decide next step, delegate if needed.

Your proposal (output the decision line only, no extra commentary):"""


def _critic_prompt(proposal_msg: A2AMessage, context: dict[str, Any]) -> str:
    """Build the user prompt for the Critic (Phase 2)."""
    proposal = proposal_msg.payload.get("proposed_action", "")
    rationale = proposal_msg.payload.get("rationale", "")
    return f"""You are the Critic. Review the Proposer's proposal against the workflow, decisions, and plan.

## Context (summary)
- Pending prompt: {json.dumps(context.get("pending_prompt", {}))[:500]}...
- Next Actions (from workspace_status): {str(context.get("workspace_status", {}).get("next_actions", ""))[:300]}

## Proposer's proposal
{proposal}
{f'Rationale: {rationale}' if rationale else ''}

---

Critique the proposal. Consider:
- Does it align with the Implementation Plan and Next Actions?
- Is it the right role for the task?
- Any re-delegation loops or missing steps?
- Does the plan say something different?

Output a brief critique (2-4 sentences). If the proposal is sound, say so. If not, suggest improvements. Output only the critique, no preamble:"""


def _synthesizer_prompt(
    proposal_msg: A2AMessage,
    critique_msg: A2AMessage,
    context: dict[str, Any],
) -> str:
    """Build the user prompt for the Synthesizer (Phase 3)."""
    proposal = proposal_msg.payload.get("proposed_action", "")
    critique = critique_msg.payload.get("critique", "")
    return f"""You are the Synthesizer. You proposed an action; the Critic has reviewed it.

## Your original proposal
{proposal}

## Critic's critique
{critique}

---

Incorporate the critique. Output the final decision—exactly one of:
1. A delegation: `/role task` (e.g. `/lead-engineer Add unit tests for health.py`)
2. User Intervention Required: [reason]
3. ORCHESTRATION_COMPLETE: [brief summary]
4. Run one cycle: get_workspace_status, read PROJECT_WORKSPACE.md, decide next step, delegate if needed.

Your final decision (output the decision line only):"""


def run_brain(
    system_message: str,
    context: dict[str, Any],
    api_key_override: Optional[str] = None,
) -> str:
    """
    Run the orchestrator brain: propose → critique → synthesize.

    Args:
        system_message: Full orchestrator system prompt (rule, patterns, workflow, decisions, roles).
        context: Dict with pending_prompt, workspace_status, workflow_config, workspace_snippet.
        api_key_override: Optional API key; if not set, uses ANTHROPIC_API_KEY or ORCHESTRATOR_LLM_API_KEY from env.

    Returns:
        Final decision string (delegation, User Intervention, ORCHESTRATION_COMPLETE, or run cycle).
    """
    result = run_brain_with_flow(system_message, context, api_key_override)
    return result["final_decision"]


def run_brain_with_flow(
    system_message: str,
    context: dict[str, Any],
    api_key_override: Optional[str] = None,
) -> dict[str, Any]:
    """
    Run the orchestrator brain and return the full A2A flow (proposal, critique, synthesis, decision).

    Args:
        system_message: Full orchestrator system prompt (rule, patterns, workflow, decisions, roles).
        context: Dict with pending_prompt, workspace_status, workflow_config, workspace_snippet.
        api_key_override: Optional API key; if not set, uses ANTHROPIC_API_KEY or ORCHESTRATOR_LLM_API_KEY from env.

    Returns:
        Dict with keys: proposal, critique, synthesis, final_decision.
    """
    task_id = f"brain-{uuid.uuid4().hex[:8]}"
    proposer_model = get_proposer_model()
    critic_model = get_critic_model()

    # Phase 1: Proposer produces initial proposal
    proposer_user = _proposer_prompt(context)
    proposal_text = _call_llm(
        proposer_model, system_message, proposer_user, api_key_override
    )
    proposal_text = proposal_text.strip()

    # Wrap in A2A message
    proposal_msg = create_proposal(
        task_id=task_id,
        proposed_action=proposal_text,
        rationale="",
        correlation_id=task_id,
    )

    # Phase 2: Critic critiques the proposal
    critic_user = _critic_prompt(proposal_msg, context)
    critique_text = _call_llm(
        critic_model, system_message, critic_user, api_key_override
    )
    critique_text = critique_text.strip()

    critique_msg = create_critique(
        task_id=task_id,
        critique_text=critique_text,
        correlation_id=task_id,
    )

    # Phase 3: Synthesizer produces final decision
    synthesizer_user = _synthesizer_prompt(proposal_msg, critique_msg, context)
    final_decision = _call_llm(
        proposer_model, system_message, synthesizer_user, api_key_override
    )
    final_decision = final_decision.strip()

    synthesis_msg = create_synthesis(
        task_id=task_id,
        final_decision=final_decision,
        correlation_id=task_id,
    )

    return {
        "proposal": proposal_msg.payload.get("proposed_action", proposal_text),
        "critique": critique_msg.payload.get("critique", critique_text),
        "synthesis": synthesis_msg.payload.get("final_decision", final_decision),
        "final_decision": synthesis_msg.payload.get("final_decision", final_decision),
    }
