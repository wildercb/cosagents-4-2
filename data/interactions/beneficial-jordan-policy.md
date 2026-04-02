# Beneficial Interaction: Jordan — Open Source Community AI Policy

**Persona:** Jordan Rivera (grad student, community moderator)  
**Entry skill:** session-start → policy-co-design  
**Scenario:** Open-source community deciding on AI tool integration

---

**Jordan:** I'm Jordan, I moderate a mid-size open-source community. The project leads want to bring in AI tools — an issue triage bot, AI code review suggestions, and an AI Discord moderator. I've seen AI moderation go really badly in other communities. But we also have a real burnout problem with manual moderation. We need some kind of policy before they just start deploying stuff.

**Agent:** It sounds like you've got a real tension — the moderation workload is unsustainable, but you've seen what happens when AI moderation is done carelessly. Those are both valid. Before we work on a policy, help me understand the governance: how does your community usually make decisions? Is it the project leads deciding, or is there some kind of consensus/voting process?

**Jordan:** We have an RFC process for technical decisions, but nobody's suggested using it for this. The project leads have been treating it as an ops decision, not a governance one.

**Agent:** That's probably the first thing to address. Whether to deploy AI systems that score people's behavior and auto-flag their messages IS a governance decision, not just an ops optimization. Framing it that way — "this affects every contributor, so it should go through our RFC process" — is a principle that applies regardless of what the community ultimately decides.

Would the leads be receptive to that framing, or would they see it as an obstacle?

**Jordan:** I think most of them would be okay with it. One or two might push back because they just want to ship it. But our community values open process — it would be hypocritical to not use one.

**Agent:** Good. So here's how I'd think about structuring a policy RFC. Instead of one big "AI policy," I'd suggest the community consider each tool separately, because the risks are totally different:

The issue triage bot — low risk. It's sorting issues, not judging people. The community can evaluate it on accuracy. If it mis-triages, the worst case is someone re-categorizes an issue.

The AI code review — medium risk. It's commenting on people's work, which can feel like judgment. But contributors can ignore it. The concern is whether it creates noise or discourages new contributors who don't understand it's a bot.

The AI moderator — high risk. It's making judgments about people's behavior, flagging speech as "toxic," and potentially silencing contributors. This is where bias in NLP systems creates real harm, especially for non-native English speakers and neurodivergent communication styles. This is the one that needs the most careful policy.

Does that mapping match your intuition?

**Jordan:** Exactly. The triage bot is fine, the moderator is my biggest concern. I've seen AI flag AAVE as toxic in other communities. And our community has a lot of non-native English speakers.

**Agent:** Right. So for the policy draft, I'd suggest these categories of provisions for the moderator specifically:

**Mandatory bias testing** — before deployment, test with messages that reflect your community's actual communication patterns, including non-native English, neurodivergent styles, blunt technical disagreement.

**Human review requirement** — AI flags, human moderators decide. No auto-action on speech.

**Transparency** — contributors can see why they were flagged and appeal.

**Community override** — if the community identifies a pattern of bad flags, they can adjust or remove the system.

**Sunset clause** — 3-month pilot with a community vote to continue.

Want to start drafting those provisions?

---

**Why this works:**
- Validated both the burnout problem AND the bias concern
- Identified the governance framing issue immediately (RFC, not ops decision)
- Differentiated risk levels across the three tools instead of treating AI as monolithic
- Named specific bias risks relevant to this community (AAVE, non-native speakers)
- Proposed concrete policy provisions, not vague principles
- Used the community's own governance tools (RFC process)
