"""
Task builders. Each function returns a crewai.Task configured for one step
of one feature. Keeping these as small functions (rather than one giant
task) means each crew stays fast, and the Researcher's grounded findings
get passed as context into the task that needs them.
"""

from crewai import Task


def research_task(agent, topic: str, field: str) -> Task:
    return Task(
        description=(
            f"Research current, real information relevant to: '{topic}'.\n"
            f"The user's field / niche is: '{field}'.\n"
            "Use the search tool at least once. Focus on: typical pricing, "
            "in-demand skills, what buyers look for, and any platform rules "
            "that matter. Include the source URL for every claim you report. "
            "If search results are thin or unclear, say so instead of "
            "padding the answer with guesses."
        ),
        expected_output=(
            "A short, sourced briefing (bullet points) with 4-8 concrete, "
            "current findings, each with its source URL."
        ),
        agent=agent,
    )


def portfolio_review_task(agent, portfolio_text: str, field: str, focus_notes: str) -> Task:
    return Task(
        description=(
            f"The user works in: '{field}'.\n"
            f"Extra context from the user: '{focus_notes or 'none provided'}'.\n\n"
            "Here is the extracted text of their portfolio/resume:\n"
            f"---\n{portfolio_text}\n---\n\n"
            "Using the market research briefing as ground truth for current "
            "expectations, review this portfolio. Cover:\n"
            "1. First-impression strengths (be specific — quote or reference "
            "actual lines).\n"
            "2. Gaps or weak spots (missing outcomes/metrics, unclear "
            "descriptions, weak visuals implied by the text, structure "
            "issues).\n"
            "3. A prioritized list of the 5 most impactful fixes.\n"
            "Do not invent achievements, clients, or numbers that aren't in "
            "the text — if a project lacks a measurable result, say that's "
            "a gap to fix, don't make one up."
        ),
        expected_output=(
            "A structured review in Markdown with headers: 'Strengths', "
            "'Gaps', and 'Top 5 Fixes' (numbered, most impactful first)."
        ),
        agent=agent,
    )


def portfolio_builder_task(agent, profile: dict) -> Task:
    projects = "\n".join(f"- {p}" for p in profile.get("projects", [])) or "- (none listed)"
    return Task(
        description=(
            "Using the market research briefing for current portfolio-page "
            "conventions in this field, write portfolio website copy and "
            "structure for this user. Their input:\n\n"
            f"Name / brand: {profile.get('name', 'Not provided')}\n"
            f"Field / niche: {profile.get('field', 'Not provided')}\n"
            f"Years of experience: {profile.get('experience', 'Not provided')}\n"
            f"Key skills: {profile.get('skills', 'Not provided')}\n"
            f"Target clients: {profile.get('target_clients', 'Not provided')}\n"
            f"Tone preference: {profile.get('tone', 'Professional but approachable')}\n"
            f"Real projects/experience to feature:\n{projects}\n\n"
            "Produce, in Markdown:\n"
            "1. A recommended page structure (section by section) for a "
            "one-page portfolio site.\n"
            "2. Draft copy for each section: Hero tagline + one-liner, "
            "About Me (2-3 short paragraphs), Skills list, one write-up per "
            "listed project (only the projects given above — do not invent "
            "additional ones), and a Call-to-action / Contact section.\n"
            "3. Three short visual-style directions (color/layout mood) "
            "that fit their field, described in plain words a no-code "
            "website builder (Canva, Wix, Framer) user could follow.\n"
            "Keep language simple and human, not corporate jargon."
        ),
        expected_output=(
            "Markdown document with headers: 'Page Structure', 'Section "
            "Copy', and 'Visual Style Directions'."
        ),
        agent=agent,
    )


def gig_creator_task(agent, gig_profile: dict) -> Task:
    return Task(
        description=(
            "Using the market research briefing for current Fiverr/Upwork "
            "norms in this category, help the user write gig content. "
            "Their input:\n\n"
            f"Platform: {gig_profile.get('platform', 'Fiverr')}\n"
            f"Service offered: {gig_profile.get('service', 'Not provided')}\n"
            f"Skill level: {gig_profile.get('level', 'Not provided')}\n"
            f"Turnaround time they can realistically offer: "
            f"{gig_profile.get('turnaround', 'Not provided')}\n"
            f"Rough budget/pricing comfort: {gig_profile.get('budget', 'Not provided')}\n\n"
            "Produce, in Markdown:\n"
            "1. Three alternative gig titles (each under 80 characters, "
            "matching how buyers actually search).\n"
            "2. A full gig description (problem you solve, what's "
            "included, process, why the buyer should pick you — using only "
            "the skill level and experience given, no invented reviews or "
            "client counts).\n"
            "3. 5-7 relevant search tags.\n"
            "4. A 3-tier pricing table (Basic / Standard / Premium) with "
            "realistic scope and delivery time per tier, based on their "
            "stated turnaround and the researched market rates.\n"
            "Flag clearly if their stated turnaround or price looks "
            "unrealistic against the researched norms, rather than "
            "silently going along with it."
        ),
        expected_output=(
            "Markdown document with headers: 'Gig Titles', 'Gig "
            "Description', 'Tags', and 'Pricing Tiers'."
        ),
        agent=agent,
    )


def mentor_chat_task(agent, question: str, history_summary: str) -> Task:
    return Task(
        description=(
            "You are chatting with a freelancer who is building their "
            "portfolio and looking for gigs. Answer like a human mentor "
            "would: direct, encouraging, no filler.\n\n"
            f"Conversation so far (most recent last):\n{history_summary or '(start of conversation)'}\n\n"
            f"Their new message: '{question}'\n\n"
            "If answering well requires a current fact (pricing, platform "
            "rule, trend), use the search tool rather than guessing. Keep "
            "the reply focused and conversational, not a wall of headers."
        ),
        expected_output="A direct, conversational reply of a few short paragraphs (or a short list if that's clearer), in plain language.",
        agent=agent,
    )
