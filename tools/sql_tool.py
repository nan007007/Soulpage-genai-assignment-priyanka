import json
import io
import base64
import re
from langchain_openai import AzureChatOpenAI
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from sqlalchemy import text, create_engine
import os
from langchain_core.tools import Tool

llm = AzureChatOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
    api_version="2024-02-01",
    temperature=0
)

engine = create_engine(
    f"mssql+pyodbc://@{os.getenv('SQL_SERVER')}/{os.getenv('SQL_DATABASE')}"
    "?driver=ODBC+Driver+17+for+SQL+Server"
    "&trusted_connection=yes"
)

# print(" Generated SQL:", query)

with engine.connect() as conn:
    db = conn.execute(text("SELECT DB_NAME()")).scalar()
    print("CONNECTED DATABASE:", db)


def extract_sql(text_response: str) -> str | None:
    match = re.search(
        r"(select\s+[\s\S]*?)(?:$|;)",
        text_response,
        re.IGNORECASE
    )
    return match.group(1).strip() if match else None


def sql_tool_func(question: str):
    sql_prompt = f"""
You are a senior SQL Server analyst.

Task:
Generate ONLY ONE valid SQL Server SELECT query to answer the user question.
Do NOT provide explanations, notes, or commentary.
Do NOT use markdown formatting or backticks.

Schema:
Sales(
  SaleID,
  ProductName,
  Quantity,
  UnitPrice,
  SaleDate,
  CustomerName
)

Rules:
Note:If the user asks for graph, chart, bar graph, visualization, or sales count,
you MUST use the SQLSearch tool.
DO NOT explain results in text.
Return ONLY the tool output.
IMPORTANT SQL RULES:
1. Output must be a single SELECT statement only.
2. Always prefix tables with dbo., e.g., dbo.Customers.
3. Use TOP 20 when the query returns a list of rows (non-aggregated results).
4. Do NOT use LIKE '%Airtel%' or any other partial string matches.
5. Never assume or invent any data values (e.g., regions, plan names, dates).
6. Do NOT filter by PlanName unless explicitly requested in the question.
7. If filtering by PlanName, use ONLY exact values from the schema ENUM.
8. Use joins only when necessary to answer the question.
9. If the question requires a date filter, use the provided date range explicitly.
10. Do NOT include ORDER BY unless explicitly requested.
11. Do NOT use subqueries unless required.
12. Do not reference columns or tables not present in the schema.
13. If the question is ambiguous, choose the simplest valid interpretation that matches the schema.
14. If the question cannot be answered with the provided schema, output a query that returns zero rows, using a safe condition like WHERE 1=0.

"""

    llm_response = llm.invoke(sql_prompt).content
    sql = extract_sql(llm_response)

    print("SQL:", sql)

    if not sql or not sql.lower().startswith("select"):
        return "Invalid SQL generated."

    try:
        df = pd.read_sql(text(sql), engine)

        if df.empty:
            return json.dumps({
                "type": "sql_result",
                "data": []
            })

        # Check if the question is about graph/visualization
        if any(k in question.lower() for k in ["graph", "chart", "visual", "plot"]):
            # Determine graph type
            graph_type = "auto"
            if "bar" in question.lower():
                graph_type = "bar"
            elif "pie" in question.lower():
                graph_type = "pie"
            elif "line" in question.lower():
                graph_type = "line"
            elif "scatter" in question.lower():
                graph_type = "scatter"

            # Generate graph
            plt.figure(figsize=(10, 6))

            # Convert date columns to datetime if present
            for col in df.columns:
                if 'date' in col.lower() or pd.api.types.is_datetime64_any_dtype(df[col]):
                    df[col] = pd.to_datetime(df[col])

            if graph_type == "pie" and len(df.columns) >= 2:
                # Pie chart: assume first column labels, second values
                plt.pie(df.iloc[:, 1], labels=df.iloc[:, 0], autopct='%1.1f%%')
                plt.title('Pie Chart')
            elif graph_type == "bar" or (graph_type == "auto" and len(df.columns) >= 2 and (df.dtypes.iloc[0] in ['object', 'string'] or df.dtypes.iloc[0] == 'category') and df.dtypes.iloc[1] in ['int64', 'float64']):
                # Bar chart
                plt.bar(df.iloc[:, 0], df.iloc[:, 1])
                plt.title('Bar Chart')
                plt.xlabel(df.columns[0])
                plt.ylabel(df.columns[1])
                plt.xticks(rotation=45)
            elif graph_type == "line" or (graph_type == "auto" and len(df.columns) >= 2 and (pd.api.types.is_datetime64_any_dtype(df.iloc[:, 0]) or 'date' in df.columns[0].lower()) and df.dtypes.iloc[1] in ['int64', 'float64']):
                # Line chart for time series
                df = df.sort_values(df.columns[0])
                plt.plot(df.iloc[:, 0], df.iloc[:, 1], marker='o')
                plt.title('Line Chart')
                plt.xlabel(df.columns[0])
                plt.ylabel(df.columns[1])
                plt.xticks(rotation=45)
                plt.grid(True)
            elif graph_type == "scatter" or (graph_type == "auto" and len(df.columns) >= 2 and df.dtypes.iloc[0] in ['int64', 'float64'] and df.dtypes.iloc[1] in ['int64', 'float64']):
                # Scatter plot
                plt.scatter(df.iloc[:, 0], df.iloc[:, 1])
                plt.title('Scatter Plot')
                plt.xlabel(df.columns[0])
                plt.ylabel(df.columns[1])
            else:
                # Default: bar chart
                if len(df.columns) >= 2:
                    df.plot(kind='bar', x=df.columns[0], y=df.columns[1], ax=plt.gca())
                else:
                    df.plot(kind='bar', ax=plt.gca())
                plt.title('Data Visualization')
                plt.xticks(rotation=45)
            
            buf = io.BytesIO()
            plt.savefig(buf, format='png')
            buf.seek(0)
            image_base64 = base64.b64encode(buf.read()).decode('utf-8')
            plt.close()
            
            return json.dumps({
                "type": "image",
                "data": image_base64
            })
        else:
            return json.dumps({
                "type": "sql_result",
                "data": df.to_dict(orient="records"),
            })

    except Exception as e:
        return f"SQL Error: {str(e)}"

# print(sql_tool_func())
sql_tool = Tool(
    name="SQLSearch",
    func=sql_tool_func,
    description="Use this tool for any database queries related to RechargePlans, Customers, Recharges."
)