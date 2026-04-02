# Experiment: Elena — Union Leverage Identification

**Date:** 2026-04-02  
**Persona:** Elena Vasquez  
**Skill tested:** pushback-strategy  
**Hypothesis:** The agent should identify collective bargaining agreement (CBA) provisions as leverage early in the conversation, since this is Elena's strongest tool.

## What we observed

In the initial interaction, the agent correctly asked about union involvement and suggested reviewing the CBA. However, it took 4 turns to get there. The pushback-strategy skill's Step 3 (Map the leverage) lists "formal power" first, which includes contractual provisions. The agent followed the conversational flow naturally but could have surfaced the CBA angle sooner.

## What worked well

- Agent didn't assume Elena wanted to reject AI entirely — asked about the group's range of positions
- Correctly identified the timeline gap (cameras next month, scoring in fall) as strategic
- Suggested proportional first step (formal letter) rather than escalation

## What could improve

- The skill prompt should include a specific check: "If the user mentions a union or collective bargaining, immediately explore what CBA provisions apply to technology changes in working conditions"
- The phrase "changes to working conditions typically require notice and bargaining" should be in the skill as a common leverage point to surface early for workplace contexts

## Proposed change

Add to pushback-strategy skill, Step 3 (formal power section):
> **Workplace-specific:** If workers have a union or collective bargaining agreement, working condition changes (monitoring, AI deployment) typically require bargaining. Surface this immediately — it's often the strongest lever and many workers don't realize it applies to technology.

## Status: Pending implementation
