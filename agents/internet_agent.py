from langchain.agents import create_agent
from tools.internet_tool import internet_tool

def create_internet_agent(llm):
    return create_agent(
        model=llm,
        tools=[internet_tool],
        system_prompt="Answer ONLY using InternetSearch."
    )
