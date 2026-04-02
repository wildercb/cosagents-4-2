# Design Insight: Unbundling AI Proposals

**Date:** 2026-04-02  
**Source:** Sarah and Jordan interactions  
**Observation:** In both the Sarah (smart city) and Jordan (open-source tools) interactions, the agent's most valuable contribution was helping the community separate a bundled AI proposal into individual systems with different risk levels.

## The insight

Vendors and deployers frequently bundle AI systems together — either as a "package deal" or by treating multiple distinct AI tools as one decision. This bundling serves the deployer (harder to reject, economies of scale) but harms the community (can't accept low-risk tools without accepting high-risk ones, can't have nuanced conversation).

**Unbundling is one of the most powerful facilitation moves this agent can make.**

- Sarah's city council was voting on traffic cameras + predictive policing + drone enforcement as one package
- Jordan's project leads were proposing issue triage + code review + moderation as one decision

In both cases, separating them revealed that some components were low-risk and potentially beneficial, while others required serious scrutiny.

## Implication for agent design

The session-start skill should include a check: "If the user describes multiple AI systems or a bundled proposal, help them separate the components before proceeding to any skill. Different components may route to different skills."

This is potentially a standalone facilitation move that should happen BEFORE any skill routing.

## Status: Insight documented, pending skill update
