from langchain.agents import create_agent
from tools.sql_tool import sql_tool_func
from langchain_core.tools import Tool

sql_tool = Tool(
    name="SQLSearch",
    func=sql_tool_func,
    description="SQL database queries + graph generation"
)

def create_sql_agent(llm):
    return create_agent(
        model=llm,
        tools=[sql_tool],
        system_prompt="""
You are a SQL execution agent.

RULES:
- ALWAYS call SQLSearch
- NEVER explain
- NEVER modify tool output
- RETURN tool output AS IS
"""
    )
