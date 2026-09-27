from litellm_patch import apply_patch
apply_patch()

from crewai import Crew, Process, LLM
from crewai import Crew, Process, LLM

from agents import build_agents
from tasks import research_task, portfolio_review_task, portfolio_builder_task, gig_creator_task, mentor_chat_task
from search_tools import DuckDuckGoSearchTool


def get_llm(api_key: str, model: str = "groq/openai/gpt-oss-120b") -> LLM:
    return LLM(
        model=model,
        api_key=api_key,
        temperature=0.6,
        max_retries=2,
    )


def _crew(agents_list, tasks_list) -> Crew:
    return Crew(
        agents=agents_list,
        tasks=tasks_list,
        process=Process.sequential,
        verbose=False,
    )


def run_portfolio_review(llm, portfolio_text: str, field: str, focus_notes: str) -> str:
    search_tool = DuckDuckGoSearchTool()
    agents = build_agents(llm, search_tool)

    t1 = research_task(agents["researcher"], topic=f"portfolio expectations in {field}", field=field)
    t2 = portfolio_review_task(agents["reviewer"], portfolio_text, field, focus_notes)
    t2.context = [t1]

    crew = _crew([agents["researcher"], agents["reviewer"]], [t1, t2])
    result = crew.kickoff()
    return str(result)


def run_portfolio_builder(llm, profile: dict) -> str:
    search_tool = DuckDuckGoSearchTool()
    agents = build_agents(llm, search_tool)

    field = profile.get("field", "freelancing")
    t1 = research_task(agents["researcher"], topic=f"portfolio page conventions in {field}", field=field)
    t2 = portfolio_builder_task(agents["builder"], profile)
    t2.context = [t1]

    crew = _crew([agents["researcher"], agents["builder"]], [t1, t2])
    result = crew.kickoff()
    return str(result)


def run_gig_creator(llm, gig_profile: dict) -> str:
    search_tool = DuckDuckGoSearchTool()
    agents = build_agents(llm, search_tool)

    platform = gig_profile.get("platform", "Fiverr")
    service = gig_profile.get("service", "")
    t1 = research_task(agents["researcher"], topic=f"{platform} gig pricing and structure for '{service}'", field=service)
    t2 = gig_creator_task(agents["gig_expert"], gig_profile)
    t2.context = [t1]

    crew = _crew([agents["researcher"], agents["gig_expert"]], [t1, t2])
    result = crew.kickoff()
    return str(result)


def run_market_research(llm, query: str, field: str = "") -> str:
    search_tool = DuckDuckGoSearchTool()
    agents = build_agents(llm, search_tool)

    t1 = research_task(agents["researcher"], topic=query, field=field or query)
    crew = _crew([agents["researcher"]], [t1])
    result = crew.kickoff()
    return str(result)


def run_mentor_chat(llm, question: str, history_summary: str) -> str:
    search_tool = DuckDuckGoSearchTool()
    agents = build_agents(llm, search_tool)

    t1 = mentor_chat_task(agents["mentor"], question, history_summary)
    crew = _crew([agents["mentor"]], [t1])
    result = crew.kickoff()
    return str(result)
