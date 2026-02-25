"""
Orchestrator brain: two-model propose → critique → synthesize flow using A2A.

Proposer (Model A): Receives context (MCP results, PROJECT_WORKSPACE), produces
initial proposal. Critic (Model B): Receives proposal, critiques it. Synthesizer
(Model A): Receives critique, produces final decision. All handoffs use A2A
message format for consistency and future extensibility.
"""

import json
import uuid
from typing import Any, AsyncIterator, Optional

from orchestrator_client.a2a import (
    A2AMessage,
    create_proposal,
    create_critique,
    create_synthesis,
)
from orchestrator_client.config import (
    get_anthropic_api_key,
    get_openai_api_key,
    get_openai_model,
    get_llm_provider,
    get_proposer_model,
    get_critic_model,
)
from orchestrator_client.llm_provider import chat_sync, chat_stream


def _resolve_keys(api_key_override: Optional[str]) -> tuple[Optional[str], Optional[str]]:
    """Resolve anthropic_key and openai_key, applying override when provided."""
    anthropic_key = api_key_override or get_anthropic_api_key()
    openai_key = api_key_override or get_openai_api_key()
    return anthropic_key, openai_key


def _proposer_prompt(context: dict[str, Any]) -> str:
    """Build the user prompt for the Proposer (Phase 1)."""
    user_msg = context.get("user_message", "")
    user_msg_section = ""
    if user_msg:
        user_msg_section = f"""
## User message (if any)
```
{user_msg}
```

"""
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
{user_msg_section}
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
    provider = get_llm_provider()
    anthropic_key, openai_key = _resolve_keys(api_key_override)
    openai_model = get_openai_model()

    # Phase 1: Proposer produces initial proposal
    proposer_user = _proposer_prompt(context)
    proposal_text = chat_sync(
        system=system_message,
        user=proposer_user,
        model=proposer_model,
        anthropic_key=anthropic_key,
        openai_key=openai_key,
        provider=provider,
        openai_fallback_model=openai_model,
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
    critique_text = chat_sync(
        system=system_message,
        user=critic_user,
        model=critic_model,
        anthropic_key=anthropic_key,
        openai_key=openai_key,
        provider=provider,
        openai_fallback_model=openai_model,
    )
    critique_text = critique_text.strip()

    critique_msg = create_critique(
        task_id=task_id,
        critique_text=critique_text,
        correlation_id=task_id,
    )

    # Phase 3: Synthesizer produces final decision
    synthesizer_user = _synthesizer_prompt(proposal_msg, critique_msg, context)
    final_decision = chat_sync(
        system=system_message,
        user=synthesizer_user,
        model=proposer_model,
        anthropic_key=anthropic_key,
        openai_key=openai_key,
        provider=provider,
        openai_fallback_model=openai_model,
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


async def run_brain_with_flow_stream(
    system_message: str,
    context: dict[str, Any],
    api_key_override: Optional[str] = None,
) -> AsyncIterator[tuple[str, str]]:
    """
    Run the orchestrator brain and yield SSE-style (event_type, content) pairs.
    Phases 1–2 stream flow.proposal.chunk, flow.critique.chunk; Phase 3 streams
    reply.chunk token-by-token, then reply.done.
    """
    task_id = f"brain-{uuid.uuid4().hex[:8]}"
    proposer_model = get_proposer_model()
    critic_model = get_critic_model()
    provider = get_llm_provider()
    anthropic_key, openai_key = _resolve_keys(api_key_override)
    openai_model = get_openai_model()

    # Phase 1: Proposer — stream token-by-token
    proposer_user = _proposer_prompt(context)
    proposer_messages = [{"role": "user", "content": proposer_user}]
    proposal_text = ""
    async for text in chat_stream(
        system=system_message,
        messages=proposer_messages,
        model=proposer_model,
        anthropic_key=anthropic_key,
        openai_key=openai_key,
        provider=provider,
        openai_fallback_model=openai_model,
    ):
        if text:
            proposal_text += text
            yield ("flow.proposal.chunk", text)
    proposal_text = proposal_text.strip()

    proposal_msg = create_proposal(
        task_id=task_id,
        proposed_action=proposal_text,
        rationale="",
        correlation_id=task_id,
    )

    # Phase 2: Critic — stream token-by-token
    critic_user = _critic_prompt(proposal_msg, context)
    critic_messages = [{"role": "user", "content": critic_user}]
    critique_text = ""
    async for text in chat_stream(
        system=system_message,
        messages=critic_messages,
        model=critic_model,
        anthropic_key=anthropic_key,
        openai_key=openai_key,
        provider=provider,
        openai_fallback_model=openai_model,
    ):
        if text:
            critique_text += text
            yield ("flow.critique.chunk", text)
    critique_text = critique_text.strip()

    critique_msg = create_critique(
        task_id=task_id,
        critique_text=critique_text,
        correlation_id=task_id,
    )

    # Phase 3: Synthesizer — stream token-by-token
    yield ("flow.synthesis", "")  # phase marker
    synthesizer_user = _synthesizer_prompt(proposal_msg, critique_msg, context)
    synthesizer_messages = [{"role": "user", "content": synthesizer_user}]
    async for text in chat_stream(
        system=system_message,
        messages=synthesizer_messages,
        model=proposer_model,
        anthropic_key=anthropic_key,
        openai_key=openai_key,
        provider=provider,
        openai_fallback_model=openai_model,
    ):
        if text:
            yield ("reply.chunk", text)
    yield ("reply.done", "")
