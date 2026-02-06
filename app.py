import os, json
from dotenv import load_dotenv
from flask import Flask, request, jsonify, send_from_directory
from langchain_openai import AzureChatOpenAI
from flask_cors import CORS

load_dotenv()
from memory import get_memory
from agents.router import detect_intent
from agents.sql_agent import create_sql_agent
from agents.policy_agent import create_policy_agent
from agents.internet_agent import create_internet_agent
from agents.travel_agent import create_travel_agent

app = Flask(__name__)

CORS(app, resources={r"/ask": {"origins": "*"}})

llm = AzureChatOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
    api_version="2024-02-01",
    temperature=0
)

agents = {
    "sql": create_sql_agent(llm),
    "policy": create_policy_agent(llm),
    "internet": create_internet_agent(llm),
    "travel": create_travel_agent(llm)
}

@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    query = data["query"]
    cid = data["conversation_id"]

    memory = get_memory(cid)
    intent = detect_intent(query)

    agent = agents[intent]
    result = agent.invoke({
        "messages": memory.messages + [{"role": "user", "content": query}]
    })

    answer = result["messages"][-1].content

    # ---- GRAPH / TABLE PASS-THROUGH ----
    try:
        parsed = json.loads(answer)
    except Exception:
        parsed = None

    if parsed and parsed.get("type") == "image":
        return jsonify({
            "type": "image",
            "image": parsed["data"],
            "answer": "Here is the graph."
        })

    if parsed and parsed.get("type") == "sql_result":
        return jsonify({
            "type": "table",
            "data": parsed["data"]
        })

    memory.add_user_message(query)
    memory.add_ai_message(answer)

    return jsonify({"answer": answer})

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')


@app.route('/index.html')
def index_html():
    return send_from_directory('.', 'index.html')

if __name__ == "__main__":
    app.run(port=5500, debug=True)
