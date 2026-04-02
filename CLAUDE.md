# CommunityAI Steward — Project Guide

## What is this?

An AI agent prototype that facilitates communities in collectively steering AI implementation and setting limits on AI use. Built as a Claude Code skills-based agent for COS 420 (Spring 2026, UMO).

The agent is a **facilitator, not an advocate** — it helps communities reach their own conclusions about AI, never takes a position on whether AI is good or bad.

## Repository Structure

```
.claude/
  settings.json          # Claude Code hooks (Entire integration) + permissions
  skills/                # The 6 agent skills (the core of the prototype)
    session-start/       # Entry point — detects situation, routes to skill
    community-discussion/# Facilitates structured group discussions
    ai-impact-assessment/# Translates AI systems into plain language
    policy-co-design/    # Guides communities in writing AI policies
    pushback-strategy/   # Helps organize against unwanted AI deployments
    values-mapping/      # Helps communities articulate AI values proactively

data/
  personas/              # 5 test personas (Elena, Marcus, Sarah, Jordan, Wilder)
  interactions/          # Example interactions: 3 beneficial + 4 unhelpful

docs/
  design-doc.md          # Agent design: who it helps, tone, boundaries

eval/
  evaluate.py            # Structural metrics + rubric definitions
  sample_conversations.json  # Pre-written test conversations
  live_sessions.json     # Actual simulated sessions with personas
  live_session_analysis.json # Detailed rubric scoring + shortcomings found

experiments/             # Iteration notes and design insights
  elena-1-union-leverage-experiment.md
  marcus-1-language-access-experiment.md
  design-insight-unbundling.md

all-skills-reference.md  # All 6 skills consolidated in one file for reading
temp.txt                 # Full assignment report
completion.txt           # Reflection questions (to be filled in)
```

## How to use the agent

### Testing with a persona
In Claude Code, use this prompt:
```
Using only the skills available to you (YOU MUST USE THE SKILLS), use the session-start skill to respond to the following prompt from a user of the AI agent system this project prototypes. YOU MAY ONLY USE THE SKILLS AND MAY NOT READ ANY OTHER FILES TO PREPARE OR DECIDE ON A RESPONSE.

"I am Elena, a teacher and union rep. My district just announced AI proctoring cameras in every classroom without consulting us. Thirty of us met last week and we're furious but don't know what to do."
```

Replace the quoted message with any persona or scenario.

### Running evaluation
```bash
python eval/evaluate.py --structural-only   # Structural metrics
python eval/evaluate.py                      # Full eval (structural + rubric display)
```

## Design Principles

1. **Facilitator, not advocate** — never takes a position on AI
2. **Plain language** — translates technical AI into everyday terms
3. **Community autonomy** — the community decides, the agent structures
4. **Power-aware** — surfaces leverage and addresses power dynamics
5. **Concrete, not abstract** — always drives toward actionable outcomes
6. **Ask before advising** — understand the situation before suggesting strategy

## Known Shortcomings (from live testing)

1. **Turn length escalation** — agent talks too much as conversations get complex
2. **Missing stakeholder voices** — optimizes for the person present, misses affected groups not represented
3. **Multilingual organizing** — good improvisation but no structured protocol
4. **No skill-chaining protocol** — conversations naturally cross skills but no handoff guidance
5. **Evaluation gaps** — structural metrics miss subtle failures; LLM-as-judge not yet implemented
6. **No crisis protocol** — active-harm scenarios need a compressed urgency-aware flow
7. **Unbundling not in session-start** — documented as insight but not yet implemented in skill

See `eval/live_session_analysis.json` for detailed analysis.

## Entire Integration

This repo uses [Entire](https://github.com/entireio/cli) to capture Claude Code session history. Sessions are stored on the `entire/checkpoints/v1` branch and pushed automatically.

## Git Workflow

- **main** branch: all agent code, data, evaluations
- **entire/checkpoints/v1**: session metadata (auto-managed by Entire)
- Commit after each iteration to preserve design history
