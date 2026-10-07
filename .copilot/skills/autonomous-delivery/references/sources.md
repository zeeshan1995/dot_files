# Official-source review

Reviewed 2026-10-01. These are engineering recommendations adapted to this user's Copilot setup, not claims that all vendors prescribe this exact seven-stage process.

| Official source | Applied here |
|---|---|
| [GitHub: CLI custom instructions](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-custom-instructions) | Concise personal routing; detailed procedures in skills. No invented precedence between personal and repository instructions. Restart/resume to refresh instructions. |
| [GitHub: adding skills](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-skills) | Personal SKILL.md locations, explicit descriptions, reference files, and a deterministic helper without broad allowed-tools grants. |
| [GitHub: custom CLI agents](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/create-custom-agents-for-cli) and [configuration](https://docs.github.com/en/copilot/reference/custom-agents-configuration) | Restricted reviewer tools; include-custom-instructions for repository conventions; explicit skill handoff and real agent contexts. |
| [GitHub: hook reference](https://docs.github.com/en/copilot/reference/hooks-reference) | Do not claim unbypassable hooks: command preToolUse timeouts fail open; stop hooks force at most eight consecutive continuations. No global hooks were silently installed. |
| [OpenAI: execution plans](https://developers.openai.com/cookbook/articles/codex_exec_plans) | Self-contained living implementation plans with concrete paths/commands, observable outcomes, incremental milestones, decision history, and recovery steps. |
| [OpenAI: skills](https://developers.openai.com/codex/skills) | Focused skills, progressive disclosure, explicit inputs/outputs, and scripts for deterministic checks rather than prose-only assurance. |
| [OpenAI: multi-agent guidance](https://developers.openai.com/codex/multi-agent) | Bounded separate contexts, concise evidence summaries, clear task ownership, caution with parallel writes, no assumption that more agents are better. |
| [Anthropic: Claude Code best practices](https://code.claude.com/docs/en/best-practices) | Explore/plan before implementation, executable verification, concise persistent instructions, independent verification, and context management. |
| [Anthropic: long-running harnesses](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) | Explicit initially-unverified feature list, incremental delivery, durable handoffs, baseline recovery checks, and real end-to-end testing rather than premature completion. |
| [Anthropic: subagents](https://code.claude.com/docs/en/sub-agents) and [agent teams](https://code.claude.com/docs/en/agent-teams) | Independent competing hypotheses, read-only critics, distinct writer ownership, bounded coordination, and token-cost awareness. |

## Deliberate choices and limits

- Five planning gates and a proposer/challenger pair at every stage are the user's requested policy. The vendor docs recommend proportional planning and selective parallelism, not universal debates. Keep each required artifact short for small tasks; never skip the requested gate.
- Two review cycles and two repair attempts are explicit local bounds to prevent endless retries, not vendor guarantees.
- The verifier is mandatory for autonomous completion. Testing applicability is fixed before implementation; missing infrastructure is not an exclusion.
- A required check cannot become not-applicable after failing. Only the documented category exclusions, with concrete repository evidence and planning review, are allowed.
- The local validator catches inconsistent/missing/stale records and source changes. It cannot authenticate model-authored reports, stop arbitrary shell writes, enforce billing, or keep a machine awake.
- Copilot, Codex, and Claude have different configuration formats and runtime semantics. This update only configures Copilot; it does not install Claude/Codex settings or assume their hooks/features exist in Copilot.
- Artifact-first delegation and bounded handoffs apply the vendors' context-isolation guidance. The 500-word worker handoff, 1,000-word coordinator capsule, and 70% reported-usage refresh trigger are local operating rules, not vendor-guaranteed context limits. Subagents can increase aggregate tokens/cost even while reducing the main session's context growth.
