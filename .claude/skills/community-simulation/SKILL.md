---
name: community-simulation
description: Run a multi-agent community deliberation simulation where personas debate, form coalitions, and vote on AI deployment proposals
user_invocable: true
---

# Community Simulation Skill

Run a swarm simulation where multiple community members deliberate on an AI deployment proposal. Members debate, form alliances, shift positions, and vote.

## When to use
- User wants to see how a community would react to an AI proposal
- User wants to test scenarios with many voices
- User wants to observe coalition formation and power dynamics
- User says "simulate", "run a simulation", "community debate", or "swarm"

## How to run

Execute the simulation script with the user's parameters:

```bash
cd /Users/wilder/dev/UMO/cosagents/4-2
python sim/simulate.py [OPTIONS]
```

### Options

| Flag | Description | Default |
|------|-------------|---------|
| `--scenario` | Predefined scenario: `classroom`, `workplace`, `smartcity`, `opensource` | `classroom` |
| `--swarm N` | Generate N community members (larger = more diverse debate) | 0 (uses existing 5 personas) |
| `--rounds N` | Number of discussion rounds | 3 |
| `--mix` | Combine existing personas WITH generated swarm members | off |
| `--proposal "..."` | Custom proposal text (overrides scenario default) | scenario default |
| `--api-key KEY` | Anthropic API key | from .env |

### Examples

**Small test with existing personas:**
```bash
python sim/simulate.py --scenario classroom --rounds 2
```

**Large swarm simulation (12 members):**
```bash
python sim/simulate.py --scenario workplace --swarm 12 --rounds 3
```

**Massive community meeting (20 members, mixed with personas):**
```bash
python sim/simulate.py --scenario smartcity --swarm 20 --mix --rounds 4
```

**Custom proposal:**
```bash
python sim/simulate.py --swarm 8 --proposal "Replace all human tutors with AI tutoring bots" --scenario classroom
```

## What it produces

1. **Live display** — Each member speaks in turn with colored stance indicators
2. **Coalition tracking** — Groups form dynamically as positions crystallize
3. **Stance shifts** — Highlighted when a member changes position mid-debate
4. **Final vote** — Tallied with shift tracking
5. **Outcome** — Approved, Rejected, Conditional, or No Consensus
6. **AI analysis** — LLM-generated summary of dynamics, turning points, power analysis
7. **Saved transcript** — JSON file in `sim/results/` for later review

## After the simulation

Present the results to the user and discuss:
- Which coalitions formed and why
- What arguments were most persuasive
- Whose voices were missing or drowned out
- How power dynamics shaped the outcome
- What the community might do differently

This connects back to the CommunityAI Steward's core mission: helping communities make informed collective decisions about AI.
