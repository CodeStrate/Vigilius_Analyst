from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from utils.app_utils import get_chinook_db_and_dialect
from prompts import SQL_SYSTEM_PROMPT

llm = ChatOpenAI(
    model="gpt-4o"
)

db, dialect = get_chinook_db_and_dialect()

toolkit = SQLDatabaseToolkit(db=db, llm=llm)

tools = toolkit.get_tools()

def get_sql_tools():
    for tool in tools:
        print(f"{tool.name} : {tool.description}\n")

nl2sql_agent = create_react_agent(
    model=llm,
    tools=tools,
    prompt=SQL_SYSTEM_PROMPT.format(dialect=dialect, top_k=5)
)

def run_agent():
    while True:
        user_input = input("User: ")
        for step in nl2sql_agent.stream(
            {"messages" : [{
                "role" : "user",
                "content" : user_input
            }]},
            stream_mode="values"
        ):
            step["messages"][-1].pretty_print()
    
if __name__ == '__main__':
    print("Welcome to NL2SQL Agent!")
    run_agent()