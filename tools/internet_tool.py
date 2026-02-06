from langchain_core.tools import Tool
from ddgs import DDGS
import json
def internet_agent_with_citations(question: str) -> dict:
    try:
        with DDGS() as ddgs:
            results = ddgs.text(question, max_results=5)
            bodies = []
            citations = []
            
            for r in results:
                if r.get("body"):
                    bodies.append(r.get("body", ""))
                    citations.append({
                        "title": r.get("title", "Web Result"),
                        "url": r.get("href", "#")
                    })
            
            answer = "\n".join(bodies) if bodies else "No internet results found."
            if citations:
                answer += "\n\n[CITATIONS_METADATA]" + json.dumps(citations) + "[/CITATIONS_METADATA]"
            return {"answer": answer, "citations": citations}
    except Exception as e:
        return {"answer": f"Internet search error: {str(e)}", "citations": []}


def internet_agent(question: str):
    result = internet_agent_with_citations(question)
    return result["answer"]


internet_tool = Tool(
    name="InternetSearch",
    func=internet_agent,
   description=(
    "Use this tool for general web searches and public information lookup using DuckDuckGo.\n"
    "Do NOT use this tool for internal company policy questions.\n"
    "Do NOT use this tool for SQL or database queries.\n"
    "Use only when no other tool is applicable.\n"
    "This tool should be used for general knowledge, definitions, news, and public resources.\n"
    "Prefer this tool when the question is not related to internal processes or data.\n"
    "Do not answer from memory; rely on search results.\n"
    "Return only concise and relevant results.\n"
    "If no results are found, respond with 'No internet results found.'\n"
    "Do not call this tool for sensitive or confidential company information.\n"
)
)
