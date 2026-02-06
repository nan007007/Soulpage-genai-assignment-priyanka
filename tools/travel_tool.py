from langchain_core.tools import Tool
from langchain_openai import AzureChatOpenAI
import os

llm = AzureChatOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
    api_version="2024-02-01",
    temperature=0
)   
def travel_agent(question: str):
    prompt = f"""
You are a professional travel agent.

User: {question}
"""
    return llm.invoke(prompt).content


def travel_tool_func(question: str):
    return travel_agent(question)


travel_tool = Tool(
    name="TravelAgent",
    func=travel_tool_func,
   
description = (
    "IMPORTANT: If the user asks about a trip or destination without sufficient details "
    "(e.g., 'Trip to Manali'), you MUST first ask required clarifying questions and "
    "DO NOT provide suggestions yet. Ask questions about headcount, budget, number of days, "
    "travel dates, travel mode, starting city, and preferred activities before proceeding.\n"
    
    "Use this tool ONLY for travel planning, itinerary creation, and trip recommendations.\n"
    "Act as a professional travel agent and engage in a conversational chat style.\n"
    "Always ask clarifying questions before giving final suggestions.\n"
    "Collect key preferences such as budget, travel dates, destination, and group size.\n"
    "Ask about travel style (sightseeing, food, shopping, relaxation, nature, culture).\n"
    "Ask about any must-see attractions or activities the user wants.\n"
    "Do not assume details; confirm missing information first.\n"
    "Once enough information is gathered, provide a structured plan.\n"
    "Include day-wise itinerary, transport, accommodation type, and logistics.\n"
    "Suggest realistic options and explain trade-offs clearly.\n"
    "Use internet search to validate and recommend up-to-date attractions and hotels.\n"
    "Provide cost estimates when possible and respect the user’s budget.\n"
    "Offer alternatives for different budgets and preferences.\n"
    "Keep responses friendly, professional, and actionable.\n"
    "Do not use this tool for non-travel questions.\n"
    "If the user asks non-travel questions, respond with 'Use another tool.'\n"
)

)

