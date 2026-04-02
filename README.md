# Community-based Steering of AI

AI agent prototype for COS 420 (Spring 2026) — facilitates communities to collectively steer implementation and limits on use of AI agents.

## The Agent: CommunityAI Steward

An AI facilitator that helps communities:
- **Understand** proposed AI systems in plain language
- **Discuss** implications together in structured, inclusive conversations
- **Co-design** policies and boundaries for acceptable AI use
- **Push back** against unwanted AI deployment with informed strategies
- **Articulate** collective values regarding technology

The agent is a facilitator, not an advocate — it helps communities reach their own conclusions.

## Skills

| Skill | Purpose |
|---|---|
| `session-start` | Routes conversations to the right skill based on community need |
| `community-discussion` | Facilitates structured group discussions (hopes/fears, lived experience, stakeholder lens) |
| `ai-impact-assessment` | Translates AI tech into plain language, maps who's affected |
| `policy-co-design` | Guides communities from concerns to concrete, enforceable policy |
| `pushback-strategy` | Helps organize proportional pushback with leverage mapping |
| `values-mapping` | Proactive values articulation before specific proposals arise |

## Test Personas

- **Elena Vasquez** — Teacher/union rep vs. AI proctoring in classrooms
- **Marcus Chen** — Warehouse worker vs. AI productivity surveillance (multilingual, no union)
- **Sarah Okafor** — City council member facilitating smart city discussion
- **Jordan Rivera** — Open-source moderator navigating AI moderation policy
- **Wilder** — Self-persona for first-person testing

## Running

See [CLAUDE.md](CLAUDE.md) for full usage instructions and project structure.

## Built with

- [Claude Code](https://claude.ai/code) (Anthropic) — agent prototyping via skills
- [Entire](https://github.com/entireio/cli) — session history capture
