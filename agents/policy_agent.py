from langchain.agents import create_agent
from tools.policy_tool import policy_tool

def create_policy_agent(llm):
    return create_agent(
        model=llm,
        tools=[policy_tool],
        system_prompt="Answer ONLY using PolicySearch."
    )
