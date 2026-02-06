import os
import json

from langchain_core.tools import Tool
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from tools.internet_tool import internet_agent_with_citations

policy_client = SearchClient(
    endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"),
    index_name=os.getenv("AZURE_SEARCH_INDEX"),
    credential=AzureKeyCredential(os.getenv("AZURE_SEARCH_KEY"))
)


def policy_tool_func(question: str) -> str:
    try:
        results = policy_client.search(search_text=question, top=5)
        docs = []
        citations = []
        sharepoint_base = os.getenv("SHAREPOINT_BASE_URL", "")
        
        for idx, r in enumerate(results):
            # print(f"\n--- Result {idx} ---")
            
            if r.get("content"):
                docs.append(r.get("content", ""))
                
                # Extract correct metadata
                file_name = r.get("metadata_spo_item_name", "Document")
                file_path = r.get("metadata_spo_item_path", "")
                
                # print(f"File name: {file_name}")
                # print(f"File path: {file_path}")
                
                # Construct proper SharePoint URL
                if sharepoint_base:
                    # Build URL from SharePoint base + Shared Documents + filename
                    source_url = f"{sharepoint_base}/{file_name}"
                else:
                    source_url = f"Internal Document: {file_name}"
                
                # print(f"Final URL: {source_url}")
                citations.append({"title": file_name, "url": source_url})

        if docs:
            answer_text = "\n".join(docs)
            # Append citations metadata to the answer for later extraction
            if citations:
                metadata = json.dumps(citations)
                answer_text += "\n\n[CITATIONS_METADATA]" + metadata + "[/CITATIONS_METADATA]"
                # print(f"Appending citations metadata: {metadata}")
            return answer_text

        result = internet_agent_with_citations(question + " government policy")
        answer_text = result["answer"]
        if result.get("citations"):
            metadata = json.dumps(result["citations"])
            answer_text += "\n\n[CITATIONS_METADATA]" + metadata + "[/CITATIONS_METADATA]"
        return answer_text

    except Exception as e:
        print(f"Policy tool error: {e}")
        result = internet_agent_with_citations(question + " government policy")
        answer_text = result["answer"]
        if result.get("citations"):
            metadata = json.dumps(result["citations"])
            answer_text += "\n\n[CITATIONS_METADATA]" + metadata + "[/CITATIONS_METADATA]"
        return answer_text

        if docs:
            answer_text = "\n".join(docs)
            # Append citations metadata to the answer for later extraction
            if citations:
                metadata = json.dumps(citations)
                answer_text += "\n\n[CITATIONS_METADATA]" + metadata + "[/CITATIONS_METADATA]"
                print(f"Appending citations metadata: {metadata}")
            return answer_text

        result = internet_agent_with_citations(question + " government policy")
        answer_text = result["answer"]
        if result.get("citations"):
            metadata = json.dumps(result["citations"])
            answer_text += "\n\n[CITATIONS_METADATA]" + metadata + "[/CITATIONS_METADATA]"
        return answer_text

    except Exception as e:
        print(f"Policy tool error: {e}")
        result = internet_agent_with_citations(question + " government policy")
        answer_text = result["answer"]
        if result.get("citations"):
            metadata = json.dumps(result["citations"])
            answer_text += "\n\n[CITATIONS_METADATA]" + metadata + "[/CITATIONS_METADATA]"
        return answer_text
        result = internet_agent_with_citations(question + " government policy")
        answer_text = result["answer"]
        if result.get("citations"):
            answer_text += "\n\n[CITATIONS_METADATA]" + json.dumps(result["citations"]) + "[/CITATIONS_METADATA]"
        return answer_text


policy_tool = Tool(
    name="PolicySearch",
    func=policy_tool_func,
   description=(
    "Use this tool ONLY for company policy or internal document queries.\n\n"
    "This tool must be triggered whenever the user asks about:\n"
    "- HR policies (leave, attendance, onboarding, termination, behavior guidelines).\n"
    "- IT policies (asset usage, device policy, remote access, password rules, email usage).\n"
    "- Security policies (data security, access control, confidentiality, information handling).\n"
    "- Compliance policies (legal compliance, code of conduct, audit requirements).\n"
    "- Leave or holiday rules (leave types, encashment, carry-forward rules, holiday calendars).\n"
    "- Any company handbook, SOP (Standard Operating Procedure), or policy document.\n"
    "- Employee benefits, pay structure rules, reimbursements, or internal process documentation.\n\n"

    "IMPORTANT RULES:\n"
    "- Use this tool ONLY for policy/document lookups — not for SQL or data-related topics.\n"
    "Every answer MUST include the exact document URL(s) that were used to generate the response.  \n"
    "If multiple documents are used, list all URLs in a \"Sources\" section.\n"
    " The final section of every response MUST be:  \n"
        "Sources: \n"
        "- <document_url_1>\n"
        "- <document_url_2> \n"

    "- Do NOT answer policy questions from memory; always use this tool for accuracy.\n"
    "- If a user request involves both policy and database information, use both tools appropriately.\n"
    "- For general questions not related to policies, DO NOT use this tool.\n\n"
            
    "Fallback Behavior:\n"
    "- If no internal policy document is found, automatically fallback to searching government rules/regulations and return those results.\n\n"

    "Examples when to use this tool:\n"
    " 'What is the work-from-home policy?'\n"
    " 'Show me the leave balance rules.'\n"
    " 'What are the IT security password requirements?'\n"
    " 'Where can I find the onboarding SOP?'\n\n"

    "Examples when NOT to use this tool:\n"
    " 'List all plan avail for recharge.' (Use SQLSearch tool)\n"
    " 'Give me recharges details.' (Use SQLSearch tool)\n"
    " 'Write a tour itinerary to London.' (Use TravelAgent tool)\n"
)

)