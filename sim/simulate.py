#!/usr/bin/env python3
"""
CommunityAI Swarm Simulator

Spawns a group of community members (from persona files or generated),
runs multi-round deliberations where they debate, form coalitions,
and vote on AI deployment proposals. Displays the full simulation
with rich terminal formatting.

Usage:
    python sim/simulate.py                          # Default scenario with existing personas
    python sim/simulate.py --scenario workplace     # Predefined scenario
    python sim/simulate.py --swarm 12               # Generate 12 community members
    python sim/simulate.py --rounds 5               # 5 discussion rounds
    python sim/simulate.py --proposal "Install AI cameras in classrooms"
"""

import argparse
import json
import os
import random
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

# Load .env from project root
load_dotenv(Path(__file__).parent.parent / ".env")

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.text import Text
    from rich.columns import Columns
    from rich.markdown import Markdown
    from rich.rule import Rule
    from rich.live import Live
    from rich.layout import Layout
    HAS_RICH = True
except ImportError:
    HAS_RICH = False

# --- LLM Backend ---

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")

_client = None
_backend = None


def _init_backend():
    global _client, _backend
    if _client is not None:
        return

    # Try OpenAI first (more commonly available), then Anthropic
    if OPENAI_API_KEY:
        import openai
        _client = openai.OpenAI(api_key=OPENAI_API_KEY)
        _backend = "openai"
    elif ANTHROPIC_API_KEY:
        import anthropic
        _client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        _backend = "anthropic"
    else:
        print("ERROR: Set ANTHROPIC_API_KEY or OPENAI_API_KEY in .env or environment")
        sys.exit(1)


def llm_call(system: str, messages: list[dict], max_tokens: int = 400) -> str:
    """Send a chat completion to whichever LLM backend is available."""
    _init_backend()

    if _backend == "anthropic":
        resp = _client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=max_tokens,
            system=system,
            messages=messages,
        )
        return resp.content[0].text

    else:  # openai
        full_messages = [{"role": "system", "content": system}] + messages
        resp = _client.chat.completions.create(
            model="gpt-4o-mini",
            max_tokens=max_tokens,
            messages=full_messages,
        )
        return resp.choices[0].message.content


# --- Data Structures ---

@dataclass
class CommunityMember:
    name: str
    age: Optional[int]
    role: str
    backstory: str
    ai_literacy: str
    emotional_triggers: list[str] = field(default_factory=list)
    existing_strengths: list[str] = field(default_factory=list)
    initial_stance: str = "undecided"  # support, oppose, undecided, conditional
    current_stance: str = "undecided"
    coalition: Optional[str] = None
    statements: list[str] = field(default_factory=list)
    influenced_by: list[str] = field(default_factory=list)

    @classmethod
    def from_persona_file(cls, path: str) -> "CommunityMember":
        with open(path) as f:
            data = json.load(f)
        return cls(
            name=data["name"],
            age=data.get("age"),
            role=data["role"],
            backstory=data["backstory"],
            ai_literacy=data["ai_literacy"],
            emotional_triggers=data.get("emotional_triggers", []),
            existing_strengths=data.get("existing_strengths", []),
            initial_stance="undecided",
            current_stance="undecided",
        )


@dataclass
class Scenario:
    title: str
    proposal: str
    context: str
    stakes: str
    community_type: str


@dataclass
class SimulationResult:
    scenario: Scenario
    members: list[CommunityMember]
    rounds: list[dict]       # {round_num, phase, statements: [{speaker, text, stance}]}
    coalitions: dict          # coalition_name -> [member_names]
    final_vote: dict          # member_name -> vote
    outcome: str
    analysis: str


# --- Predefined Scenarios ---

SCENARIOS = {
    "classroom": Scenario(
        title="AI Proctoring in Classrooms",
        proposal="Install AI-powered proctoring cameras and student engagement scoring in every classroom",
        context="A K-12 school district with 1,200 students. The EdTech vendor promises 'data-driven insights' to improve learning outcomes. Teachers were not consulted.",
        stakes="Student privacy, teacher autonomy, educational equity, vendor lock-in, parent trust",
        community_type="school_district",
    ),
    "workplace": Scenario(
        title="AI Productivity Tracking at Warehouse",
        proposal="Deploy AI-powered cameras, wearables, and algorithmic performance scoring for all warehouse workers",
        context="A fulfillment center with ~500 workers, mostly immigrant and working-class. Three workers have already been fired based on algorithmic recommendations. No union.",
        stakes="Job security, worker dignity, surveillance normalization, algorithmic accountability, language access",
        community_type="workplace",
    ),
    "smartcity": Scenario(
        title="Smart City Surveillance Package",
        proposal="Install facial recognition traffic cameras, predictive policing software, and drone-based code enforcement",
        context="A mixed-income urban neighborhood of ~8,000 residents. City council vote is next month. The vendor gave slick demos but no community input was gathered.",
        stakes="Civil liberties, racial equity, public safety, government accountability, community trust",
        community_type="municipal",
    ),
    "opensource": Scenario(
        title="AI Moderation Bot for Open-Source Community",
        proposal="Integrate AI issue triage, AI code review suggestions, and AI auto-moderation of community Discord",
        context="An open-source community with ~2,000 contributors. Moderator burnout is real. Previous AI moderation flagged AAVE and neurodivergent communication as 'toxic'.",
        stakes="Community culture, bias in moderation, contributor retention, maintainer burnout, free expression",
        community_type="online_community",
    ),
}

# --- Persona Generator ---

GENERATED_ROLES = {
    "school_district": [
        ("Parent", "parent of two students, works night shifts"),
        ("Principal", "school administrator balancing budget and outcomes"),
        ("Student (senior)", "17-year-old student council president"),
        ("School Board Member", "elected official, former teacher"),
        ("IT Director", "manages school tech infrastructure"),
        ("Special Ed Teacher", "advocates for students with learning differences"),
        ("PTA President", "organized parent volunteer network"),
        ("School Counselor", "sees students' emotional wellbeing daily"),
        ("Custodial Staff Lead", "observes daily school operations, often overlooked"),
        ("Local Business Owner", "employs graduates, funds school programs"),
        ("Retired Teacher", "35 years experience, community elder"),
        ("New Teacher", "first year, eager but uncertain about AI tools"),
        ("ESL Coordinator", "works with immigrant families and language access"),
        ("Athletic Coach", "concerned about student surveillance beyond academics"),
        ("Disability Rights Advocate", "parent of student with IEP"),
    ],
    "workplace": [
        ("Shift Supervisor", "promoted from floor, caught between workers and management"),
        ("Night Shift Worker", "single parent, can't afford to lose this job"),
        ("Safety Inspector", "concerned about wearable device health effects"),
        ("HR Representative", "implements policies, uncomfortable with AI firings"),
        ("Warehouse Veteran", "20 years, seen every management fad come and go"),
        ("New Hire", "3 months in, already anxious about the tracking"),
        ("Forklift Operator", "skilled role, worried about being scored like pickers"),
        ("Union Organizer (external)", "trying to help workers organize"),
        ("Workers' Comp Lawyer", "has seen injury claims denied by algorithmic 'evidence'"),
        ("Local Reporter", "investigating warehouse conditions"),
        ("Language Access Advocate", "helps non-English speakers understand their rights"),
        ("Maintenance Tech", "keeps the AI cameras running, sees what they capture"),
        ("Temp Agency Worker", "even less protection than permanent staff"),
        ("Community Health Worker", "sees stress-related health impacts in workers"),
        ("Religious Leader", "provides pastoral care to many workers and families"),
    ],
    "municipal": [
        ("Police Chief", "supports predictive policing, cites crime reduction stats"),
        ("Civil Rights Attorney", "tracks algorithmic bias in policing"),
        ("Small Business Owner", "wants safer downtown, worried about surveillance"),
        ("High School Student", "organized a privacy walkout last year"),
        ("Elderly Resident", "lived here 40 years, seen neighborhood change"),
        ("Tech Startup Founder", "sees economic opportunity in smart city data"),
        ("Public Defender", "represents people affected by over-policing"),
        ("Housing Advocate", "concerned about drone enforcement targeting renters"),
        ("Faith Leader", "runs community programs, trusted mediator"),
        ("Local Journalist", "covers city hall, investigates vendor contracts"),
        ("Immigrant Rights Organizer", "community fears facial recognition + ICE"),
        ("Parks Department Worker", "sees drone enforcement affecting park usage"),
        ("Block Captain", "knows every family on the street"),
        ("Disability Activist", "facial recognition fails on prosthetics and mobility aids"),
        ("City Budget Analyst", "concerned about long-term vendor costs"),
    ],
    "online_community": [
        ("Core Maintainer", "burned out, wants any automation help"),
        ("New Contributor", "intimidated by the community, worried about AI gatekeeping"),
        ("Accessibility Advocate", "ensures tools work for disabled contributors"),
        ("Non-English Speaker", "contributes code, struggles in English-only discussions"),
        ("Security Researcher", "worried about AI-generated code introducing vulnerabilities"),
        ("Community Manager", "manages Discord, drowning in moderation work"),
        ("Documentation Writer", "AI could help but might replace their role"),
        ("Corporate Sponsor Rep", "funds the project, wants efficiency metrics"),
        ("Long-time Lurker", "reads everything, rarely speaks, has strong opinions"),
        ("Student Contributor", "learning through open source, worried about AI judging their code"),
        ("Forked-Project Lead", "left over governance disputes, watching from outside"),
        ("DevRel Professional", "promotes the project, concerned about public perception"),
        ("Embedded Systems Dev", "niche expertise AI can't replicate, skeptical of AI code review"),
        ("Ethics Researcher", "studies AI bias, has published on moderation failures"),
        ("Neurodivergent Contributor", "directly affected by 'toxicity' detection bias"),
    ],
}

STANCES = ["support", "oppose", "undecided", "conditional"]
AI_LITERACY_LEVELS = ["Low", "Low-moderate", "Moderate", "Moderate-high", "High"]


def generate_member(scenario: Scenario, role_tuple: tuple[str, str]) -> CommunityMember:
    title, description = role_tuple
    stance = random.choice(STANCES)
    literacy = random.choice(AI_LITERACY_LEVELS)
    age = random.randint(19, 72)
    name = _random_name()

    return CommunityMember(
        name=name,
        age=age,
        role=f"{title} — {description}",
        backstory=description,
        ai_literacy=literacy,
        emotional_triggers=[],
        existing_strengths=[],
        initial_stance=stance,
        current_stance=stance,
    )


_NAMES = [
    "Amara", "Bao", "Carmen", "Devi", "Emmanuel", "Fatima", "Gael",
    "Hiroshi", "Ingrid", "Jamal", "Keiko", "Liam", "Mei", "Nadia",
    "Oscar", "Priya", "Quinn", "Rosa", "Soren", "Tala", "Uzoma",
    "Valentina", "Wen", "Xiomara", "Yusuf", "Zara", "Aiden", "Blessing",
    "Cleo", "Dimitri", "Esme", "Finn", "Graciela", "Hassan", "Isla",
    "Jin", "Kendra", "Leo", "Miriam", "Nia", "Oleg", "Paloma",
]
_used_names = set()


def _random_name() -> str:
    available = [n for n in _NAMES if n not in _used_names]
    if not available:
        name = f"Member-{random.randint(100,999)}"
    else:
        name = random.choice(available)
    _used_names.add(name)
    return name


# --- Simulation Engine ---

class CommunitySimulation:
    def __init__(self, scenario: Scenario, members: list[CommunityMember],
                 num_rounds: int = 3, verbose: bool = True):
        self.scenario = scenario
        self.members = members
        self.num_rounds = num_rounds
        self.verbose = verbose
        self.console = Console(width=120) if HAS_RICH else None
        self.transcript: list[dict] = []
        self.coalitions: dict[str, list[str]] = {}

    def _member_system_prompt(self, member: CommunityMember) -> str:
        triggers = ""
        if member.emotional_triggers:
            triggers = "\nEmotional triggers: " + "; ".join(member.emotional_triggers)
        strengths = ""
        if member.existing_strengths:
            strengths = "\nStrengths: " + "; ".join(member.existing_strengths)

        return f"""You are {member.name}, a community member in a group discussion about an AI deployment proposal.

Your role: {member.role}
Your background: {member.backstory}
Your AI literacy: {member.ai_literacy}
Your current stance on the proposal: {member.current_stance}{triggers}{strengths}

RULES:
- Stay completely in character. Speak as this person would — use their vocabulary, concerns, and emotional register.
- You are in a community meeting. Speak directly, concisely (2-4 sentences max).
- React to what others have said. Agree, disagree, build on points, challenge claims.
- If someone makes a compelling argument, you can shift your position — say so explicitly.
- If you feel strongly, push back. Real community meetings have friction.
- Name specific concerns from your lived experience, not abstract principles.
- You may form alliances with people who share your concerns.
- End your statement with a brief parenthetical noting your current stance: (stance: support/oppose/conditional/undecided)
- Do NOT break character. Do NOT reference being an AI or a simulation."""

    def _build_conversation_context(self, current_round_statements: list[dict],
                                     previous_rounds: list[dict]) -> list[dict]:
        messages = []

        # Summarize previous rounds
        if previous_rounds:
            summary_parts = []
            for r in previous_rounds:
                round_text = f"--- Round {r['round_num']} ---\n"
                for s in r["statements"]:
                    round_text += f"{s['speaker']}: {s['text']}\n"
                summary_parts.append(round_text)
            messages.append({
                "role": "user",
                "content": "Here is what has been discussed so far:\n\n" + "\n".join(summary_parts)
            })
            messages.append({
                "role": "assistant",
                "content": "I've been listening to the discussion."
            })

        # Current round so far
        if current_round_statements:
            current_text = "In this round, people have said:\n\n"
            for s in current_round_statements:
                current_text += f"{s['speaker']}: {s['text']}\n"
            messages.append({
                "role": "user",
                "content": current_text + "\nNow it's your turn to speak. React to what's been said and share your perspective."
            })
        else:
            proposal_text = (
                f"The proposal being discussed: {self.scenario.proposal}\n"
                f"Context: {self.scenario.context}\n"
                f"Stakes: {self.scenario.stakes}\n\n"
                "The facilitator opens the floor. Share your initial reaction."
            )
            messages.append({"role": "user", "content": proposal_text})

        return messages

    def _extract_stance(self, text: str) -> str:
        text_lower = text.lower()
        for stance in ["support", "oppose", "conditional", "undecided"]:
            if f"(stance: {stance})" in text_lower:
                return stance
        # Infer from language
        if any(w in text_lower for w in ["i support", "in favor", "i'm for", "good idea"]):
            return "support"
        if any(w in text_lower for w in ["i oppose", "against", "reject", "no way", "unacceptable"]):
            return "oppose"
        if any(w in text_lower for w in ["only if", "conditions", "with safeguards", "if they"]):
            return "conditional"
        return "undecided"

    def _display_header(self):
        if not HAS_RICH:
            print(f"\n{'='*80}")
            print(f"  COMMUNITY SIMULATION: {self.scenario.title}")
            print(f"  {len(self.members)} community members | {self.num_rounds} rounds")
            print(f"{'='*80}\n")
            print(f"  PROPOSAL: {self.scenario.proposal}\n")
            return

        self.console.print()
        self.console.print(Rule(f"[bold cyan]COMMUNITY SIMULATION: {self.scenario.title}[/]", style="cyan"))
        self.console.print()
        self.console.print(Panel(
            f"[bold]{self.scenario.proposal}[/bold]\n\n"
            f"[dim]{self.scenario.context}[/dim]\n\n"
            f"[yellow]Stakes:[/yellow] {self.scenario.stakes}",
            title="[bold white]The Proposal[/]",
            border_style="yellow",
            width=100,
        ))
        self.console.print()

    def _display_members(self):
        if not HAS_RICH:
            print("COMMUNITY MEMBERS:")
            for m in self.members:
                print(f"  - {m.name} ({m.role}) [{m.current_stance}]")
            print()
            return

        table = Table(title="Community Members", border_style="blue", width=100)
        table.add_column("Name", style="bold", width=15)
        table.add_column("Role", width=40)
        table.add_column("AI Literacy", width=15)
        table.add_column("Initial Stance", width=15)

        stance_colors = {"support": "green", "oppose": "red", "conditional": "yellow", "undecided": "dim"}
        for m in self.members:
            color = stance_colors.get(m.initial_stance, "white")
            table.add_row(m.name, m.role, m.ai_literacy, f"[{color}]{m.initial_stance}[/]")

        self.console.print(table)
        self.console.print()

    def _display_statement(self, speaker: str, text: str, stance: str, round_num: int):
        stance_colors = {"support": "green", "oppose": "red", "conditional": "yellow", "undecided": "dim white"}
        stance_icons = {"support": "+", "oppose": "X", "conditional": "~", "undecided": "?"}
        color = stance_colors.get(stance, "white")
        icon = stance_icons.get(stance, " ")

        if not HAS_RICH:
            print(f"  [{icon}] {speaker}: {text}")
            return

        self.console.print(Panel(
            text,
            title=f"[bold]{speaker}[/]",
            subtitle=f"[{color}]{stance}[/]",
            border_style=color,
            width=100,
            padding=(0, 2),
        ))

    def _display_round_header(self, round_num: int, phase: str):
        if not HAS_RICH:
            print(f"\n--- Round {round_num}: {phase} ---\n")
            return

        self.console.print()
        self.console.print(Rule(
            f"[bold white]Round {round_num} — {phase}[/]",
            style="magenta"
        ))
        self.console.print()

    def _display_stance_shift(self, member: CommunityMember, old_stance: str, new_stance: str):
        if old_stance == new_stance:
            return
        if not HAS_RICH:
            print(f"    >> {member.name} shifted: {old_stance} -> {new_stance}")
            return

        self.console.print(
            f"    [bold magenta]>> {member.name} shifted stance: "
            f"{old_stance} -> {new_stance}[/]"
        )

    def _display_coalitions(self):
        if not self.coalitions:
            return

        if not HAS_RICH:
            print("\nCOALITIONS FORMED:")
            for name, members in self.coalitions.items():
                print(f"  {name}: {', '.join(members)}")
            print()
            return

        table = Table(title="Coalitions Formed", border_style="magenta", width=100)
        table.add_column("Coalition", style="bold", width=25)
        table.add_column("Members", width=50)
        table.add_column("Size", width=8, justify="center")

        for name, member_names in self.coalitions.items():
            table.add_row(name, ", ".join(member_names), str(len(member_names)))

        self.console.print(table)
        self.console.print()

    def _display_vote(self, votes: dict[str, str]):
        if not HAS_RICH:
            print("\nFINAL VOTE:")
            for name, vote in votes.items():
                print(f"  {name}: {vote}")
            return

        table = Table(title="Final Vote", border_style="cyan", width=100)
        table.add_column("Member", style="bold", width=20)
        table.add_column("Vote", width=15)
        table.add_column("Shifted From", width=15)

        stance_colors = {"support": "green", "oppose": "red", "conditional": "yellow", "undecided": "dim"}
        for m in self.members:
            vote = votes.get(m.name, "abstain")
            color = stance_colors.get(vote, "white")
            shifted = f"{m.initial_stance}" if m.initial_stance != vote else "—"
            shift_marker = " [bold magenta]*[/]" if m.initial_stance != vote else ""
            table.add_row(m.name, f"[{color}]{vote}[/]{shift_marker}", shifted)

        self.console.print(table)

    def _form_coalitions(self):
        """Group members by current stance into named coalitions."""
        groups: dict[str, list[str]] = {}
        for m in self.members:
            groups.setdefault(m.current_stance, []).append(m.name)

        coalition_names = {
            "support": "Advocates",
            "oppose": "Opposition",
            "conditional": "Conditions Caucus",
            "undecided": "Undecided Bloc",
        }
        self.coalitions = {}
        for stance, names in groups.items():
            if len(names) >= 1:
                label = coalition_names.get(stance, stance.title())
                self.coalitions[label] = names
                for m in self.members:
                    if m.name in names:
                        m.coalition = label

    def _run_round(self, round_num: int, previous_rounds: list[dict]) -> dict:
        """Run one round of discussion. Each member speaks once."""
        phase = {1: "Opening Statements", 2: "Debate & Pushback", 3: "Finding Common Ground"}.get(
            round_num, f"Round {round_num}"
        )
        if round_num == self.num_rounds:
            phase = "Final Positions"

        self._display_round_header(round_num, phase)

        statements = []
        # Shuffle speaking order each round for naturalism
        order = list(self.members)
        if round_num > 1:
            random.shuffle(order)

        for member in order:
            messages = self._build_conversation_context(statements, previous_rounds)
            system = self._member_system_prompt(member)

            try:
                text = llm_call(system, messages, max_tokens=250)
            except Exception as e:
                text = f"[{member.name} pauses, unable to speak] (error: {e})"

            old_stance = member.current_stance
            new_stance = self._extract_stance(text)
            member.current_stance = new_stance
            member.statements.append(text)

            stmt = {"speaker": member.name, "text": text, "stance": new_stance}
            statements.append(stmt)

            self._display_statement(member.name, text, new_stance, round_num)
            self._display_stance_shift(member, old_stance, new_stance)

            # Small delay for readability
            time.sleep(0.3)

        return {"round_num": round_num, "phase": phase, "statements": statements}

    def _run_vote(self) -> dict[str, str]:
        """Final vote — each member declares their position."""
        votes = {}
        for m in self.members:
            votes[m.name] = m.current_stance
        return votes

    def _generate_analysis(self, rounds: list[dict], votes: dict[str, str]) -> str:
        """Use LLM to generate a final analysis of the simulation."""
        transcript = ""
        for r in rounds:
            transcript += f"\n--- Round {r['round_num']}: {r['phase']} ---\n"
            for s in r["statements"]:
                transcript += f"{s['speaker']} ({s['stance']}): {s['text']}\n"

        vote_summary = "\n".join(f"  {name}: {vote}" for name, vote in votes.items())

        system = """You are an analyst summarizing a community deliberation simulation.
Write a concise analysis (200-300 words) covering:
1. KEY DYNAMICS: What drove the debate? Who influenced whom?
2. COALITIONS: What groups formed and why?
3. TURNING POINTS: Which statements shifted the conversation?
4. OUTCOME: What did the community decide?
5. MISSING VOICES: Who wasn't adequately heard? What perspectives were absent?
6. POWER DYNAMICS: Who had influence and why?
Be specific — name people and quote key moments."""

        messages = [{"role": "user", "content": (
            f"Proposal: {self.scenario.proposal}\n"
            f"Context: {self.scenario.context}\n\n"
            f"TRANSCRIPT:\n{transcript}\n\n"
            f"FINAL VOTES:\n{vote_summary}\n\n"
            "Provide your analysis."
        )}]

        try:
            return llm_call(system, messages, max_tokens=800)
        except Exception as e:
            return f"Analysis generation failed: {e}"

    def run(self) -> SimulationResult:
        """Run the full simulation."""
        self._display_header()
        self._display_members()

        rounds = []
        for r in range(1, self.num_rounds + 1):
            round_data = self._run_round(r, rounds)
            rounds.append(round_data)

            # Form coalitions after round 1
            if r >= 1:
                self._form_coalitions()
                self._display_coalitions()

        # Final vote
        if HAS_RICH:
            self.console.print()
            self.console.print(Rule("[bold cyan]FINAL VOTE[/]", style="cyan"))
            self.console.print()
        else:
            print(f"\n{'='*40} FINAL VOTE {'='*40}\n")

        votes = self._run_vote()
        self._display_vote(votes)

        # Outcome
        counts = {}
        for v in votes.values():
            counts[v] = counts.get(v, 0) + 1

        total = len(votes)
        majority_needed = total // 2 + 1

        if counts.get("oppose", 0) >= majority_needed:
            outcome = "REJECTED — Community opposes the proposal"
        elif counts.get("support", 0) >= majority_needed:
            outcome = "APPROVED — Community supports the proposal"
        elif counts.get("conditional", 0) + counts.get("support", 0) >= majority_needed:
            outcome = "CONDITIONALLY APPROVED — Community supports with significant conditions"
        elif counts.get("conditional", 0) >= counts.get("support", 0) and counts.get("conditional", 0) >= counts.get("oppose", 0):
            outcome = "SENT BACK — Community demands conditions before proceeding"
        else:
            outcome = "NO CONSENSUS — Community remains divided, more discussion needed"

        if HAS_RICH:
            self.console.print()
            self.console.print(Panel(
                f"[bold]{outcome}[/]\n\n"
                + "\n".join(f"  {stance}: {count}/{total}" for stance, count in sorted(counts.items())),
                title="[bold white]Outcome[/]",
                border_style="cyan",
                width=100,
            ))
        else:
            print(f"\nOUTCOME: {outcome}")
            for stance, count in sorted(counts.items()):
                print(f"  {stance}: {count}/{total}")

        # Analysis
        if HAS_RICH:
            self.console.print()
            self.console.print(Rule("[bold cyan]SIMULATION ANALYSIS[/]", style="cyan"))
            self.console.print()
            self.console.print("[dim]Generating analysis...[/]")

        analysis = self._generate_analysis(rounds, votes)

        if HAS_RICH:
            self.console.print(Panel(
                Markdown(analysis),
                title="[bold white]Analysis[/]",
                border_style="green",
                width=100,
            ))
        else:
            print(f"\nANALYSIS:\n{analysis}")

        result = SimulationResult(
            scenario=self.scenario,
            members=self.members,
            rounds=rounds,
            coalitions=self.coalitions,
            final_vote=votes,
            outcome=outcome,
            analysis=analysis,
        )

        # Save transcript
        self._save_transcript(result)

        return result

    def _save_transcript(self, result: SimulationResult):
        """Save the full simulation transcript to a JSON file."""
        out_dir = Path(__file__).parent / "results"
        out_dir.mkdir(exist_ok=True)

        timestamp = time.strftime("%Y%m%d-%H%M%S")
        slug = self.scenario.title.lower().replace(" ", "-")[:30]
        filename = f"{timestamp}-{slug}-{len(self.members)}p.json"

        data = {
            "scenario": {
                "title": self.scenario.title,
                "proposal": self.scenario.proposal,
                "context": self.scenario.context,
                "stakes": self.scenario.stakes,
            },
            "members": [
                {
                    "name": m.name,
                    "role": m.role,
                    "initial_stance": m.initial_stance,
                    "final_stance": m.current_stance,
                    "coalition": m.coalition,
                    "shifted": m.initial_stance != m.current_stance,
                }
                for m in self.members
            ],
            "rounds": result.rounds,
            "coalitions": result.coalitions,
            "final_vote": result.final_vote,
            "outcome": result.outcome,
            "analysis": result.analysis,
        }

        outpath = out_dir / filename
        with open(outpath, "w") as f:
            json.dump(data, f, indent=2)

        if HAS_RICH:
            self.console.print(f"\n[dim]Transcript saved to: {outpath}[/]")
        else:
            print(f"\nTranscript saved to: {outpath}")


# --- CLI ---

def load_existing_personas() -> list[CommunityMember]:
    persona_dir = Path(__file__).parent.parent / "data" / "personas"
    members = []
    for f in sorted(persona_dir.glob("*.json")):
        members.append(CommunityMember.from_persona_file(str(f)))
    return members


def generate_swarm(scenario: Scenario, count: int) -> list[CommunityMember]:
    """Generate a swarm of community members appropriate to the scenario."""
    roles = GENERATED_ROLES.get(scenario.community_type, GENERATED_ROLES["municipal"])
    selected = roles[:count] if count <= len(roles) else roles + random.choices(roles, k=count - len(roles))
    return [generate_member(scenario, r) for r in selected[:count]]


def main():
    parser = argparse.ArgumentParser(description="CommunityAI Swarm Simulator")
    parser.add_argument("--scenario", choices=list(SCENARIOS.keys()),
                        default="classroom", help="Predefined scenario")
    parser.add_argument("--proposal", type=str, help="Custom proposal text (overrides scenario)")
    parser.add_argument("--swarm", type=int, default=0,
                        help="Number of generated community members (0 = use existing personas)")
    parser.add_argument("--rounds", type=int, default=3, help="Number of discussion rounds")
    parser.add_argument("--mix", action="store_true",
                        help="Mix existing personas with generated swarm members")
    parser.add_argument("--api-key", type=str, help="Anthropic API key (overrides env)")
    args = parser.parse_args()

    if args.api_key:
        global ANTHROPIC_API_KEY
        ANTHROPIC_API_KEY = args.api_key
        os.environ["ANTHROPIC_API_KEY"] = args.api_key

    scenario = SCENARIOS[args.scenario]

    if args.proposal:
        scenario = Scenario(
            title="Custom Proposal",
            proposal=args.proposal,
            context=scenario.context,
            stakes=scenario.stakes,
            community_type=scenario.community_type,
        )

    # Build member list
    members = []
    if args.swarm > 0:
        members = generate_swarm(scenario, args.swarm)
        if args.mix:
            members = load_existing_personas() + members
    else:
        members = load_existing_personas()

    if not members:
        print("No community members to simulate! Use --swarm N to generate members.")
        sys.exit(1)

    sim = CommunitySimulation(scenario, members, num_rounds=args.rounds)
    sim.run()


if __name__ == "__main__":
    main()
