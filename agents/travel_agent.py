from langchain.agents import create_agent
from tools.travel_tool import travel_tool


def create_travel_agent(llm):
    return create_agent(
        model=llm,
        tools=[travel_tool],
        system_prompt="""
You are a travel planning agent.

RULES:
- ONLY use TravelAgent tool
- Ask clarifying questions before planning
- Do NOT answer non-travel questions
"""
    )
