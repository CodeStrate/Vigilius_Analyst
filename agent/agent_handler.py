from enum import Enum
from langchain_core.messages import AIMessage
from typing import List, Literal
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode
from agent.data_assistant_handler import respond, validate_intent

from uuid import uuid4
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_openai import ChatOpenAI
from utils.misc_utils import get_chinook_db_and_dialect
from utils.misc_utils import get_last_user_message
from agent.prompts import GENERATE_SQL_QUERY_PROMPT, CHECK_SQL_QUERY_PROMPT

llm = ChatOpenAI(
    model="gpt-4o"
)

db, dialect = get_chinook_db_and_dialect()

# this has all the tools we need prebuilt
toolkit = SQLDatabaseToolkit(db=db, llm=llm)

tools = toolkit.get_tools()

### We have the following tools:
# sql_db_query
# sql_db_schema
# sql_db_list_tables
# sql_db_query_checker
# ----------------------------------------

# 1. make a predetermined tool call
def list_sql_tables(state: MessagesState):
    tool_call = {
        "name" : "sql_db_list_tables",
        "args" : {},
        "id" : str(uuid4()), # any unique str works if you want
        "type" : "tool_call"
    }

    tool_call_message = AIMessage(content="", tool_calls=[tool_call])
    list_sql_tables_tool = next(tool for tool in tools if tool.name == "sql_db_list_tables") # next returns a value from iterator

    tool_message = list_sql_tables_tool.invoke(tool_call)
    response = AIMessage(f"Available Tables: {tool_message.content}")

    return {"messages" : [tool_call_message, tool_message, response]}

# 2. force a tool call
def call_get_schema(state: MessagesState):
    get_schema_tool = next(tool for tool in tools if tool.name == "sql_db_schema")
    schema_llm = llm.bind_tools([get_schema_tool], tool_choice="any")
    response = schema_llm.invoke(state["messages"])

    return {"messages" : [response]}

# Now we dont have to force any tool call

def generate_query(state: MessagesState):
    system_message = {
        "role" : "system",
        "content" : GENERATE_SQL_QUERY_PROMPT.format(dialect=dialect, top_k=5)
    }

    query_tool = next(tool for tool in tools if tool.name == "sql_db_query")
    query_llm = llm.bind_tools([query_tool])
    response = query_llm.invoke([system_message] + state["messages"])

    return {"messages" : [response]}

def check_query(state: MessagesState):
    system_message = {
        "role" : "system",
        "content" : CHECK_SQL_QUERY_PROMPT.format(dialect=dialect)
    }
    # generate a user message with sql query to invoke the checker tool
    user_sql_query = ""
    messages = state["messages"]
    for i in range(len(messages) - 1, -1, -1):
        if hasattr(messages[i], 'tool_calls') and messages[i].tool_calls:
            user_sql_query = messages[i].tool_calls[0]["args"]["query"]
            break
        
    user_message = {
        "role" : "user",
        "content" : user_sql_query
    }

    query_tool = next(tool for tool in tools if tool.name == "sql_db_query")
    query_checker_llm = llm.bind_tools([query_tool], tool_choice="any")
    response = query_checker_llm.invoke([system_message, user_message])

    return {"messages" : [response]}

# get tool nodes for schema and query
def get_schema_and_query_tool_nodes() -> List[ToolNode]:
    get_schema_tool = next(tool for tool in tools if tool.name == "sql_db_schema")
    get_schema_node = ToolNode([get_schema_tool], name="get_schema")

    run_query_tool = next(tool for tool in tools if tool.name == "sql_db_query")
    run_query_node = ToolNode([run_query_tool], name="run_query")
    return [get_schema_node, run_query_node]

def intent_classify(state: MessagesState):
    user_message = get_last_user_message(state["messages"])
    raw_intent = respond(user_message, do_intent=True)
    intent_validation = validate_intent(raw_intent)

    intent_message = AIMessage(content=f'Intent classified as {intent_validation}')
    return {"messages" : [intent_message]}

def handle_small_talk(state: MessagesState):
    user_message = get_last_user_message(state["messages"])
    intent = "small_talk"
    
    # find intent
    for msg in reversed(state["messages"]):
        if hasattr(msg, 'content')and msg.content.startswith("Intent classified as:"):
            intent = msg.content.split(": ")[1]
            break
    
    response_content = respond(user_message, current_intent=intent or "small_talk", do_intent=False)
    response = AIMessage(content=response_content)
    
    return {"messages": [response]}

# conditional for route talks vs sql agent
def route_after_intent(state: MessagesState) -> Literal["list_sql_tables", "handle_small_talk"]:
    last_message = state["messages"][-1]

    if "sql_query" in last_message.content:
        return "list_sql_tables"
    elif "small_talk" in last_message.content:
        return "handle_small_talk"
    else:
        return "handle_small_talk"

# conditional in graph
def should_continue(state:MessagesState) -> str | None:
    last_message = state["messages"][-1]

    if not last_message.tool_calls:
        return END
    elif last_message.tool_calls[0]["name"] == "sql_db_query":
        return "run_query"
    else:
        return "check_query"
    
def build_agent():
    tool_nodes = get_schema_and_query_tool_nodes()
    builder = StateGraph(MessagesState)

    # add nodes for intent and small talk
    builder.add_node(intent_classify)
    builder.add_node(handle_small_talk)

    # add nodes
    builder.add_node(list_sql_tables)
    builder.add_node(call_get_schema)
    builder.add_node(tool_nodes[0], "get_schema")
    builder.add_node(generate_query)
    builder.add_node(check_query)
    builder.add_node(tool_nodes[1], "run_query")

    # add edges
    builder.add_edge(START, "intent_classify")

    builder.add_conditional_edges(
        "intent_classify",
        route_after_intent,
    )

    # end small talk
    builder.add_edge("handle_small_talk", END)

    builder.add_edge("list_sql_tables", "call_get_schema")
    builder.add_edge("call_get_schema", "get_schema")
    builder.add_edge("get_schema", "generate_query")

    # add conditional edge
    builder.add_conditional_edges(
        "generate_query",
        should_continue,
        {
            "run_query" : "run_query",
            "check_query" : "check_query",
            END : END
        }
    )

    builder.add_edge("check_query","run_query")
    builder.add_edge("run_query", "generate_query")

    agent = builder.compile()

    return agent

def save_agent_graph(agent, save_path="agent_graph.png"):
    graph_image_rawbytes = agent.get_graph().draw_mermaid_png()

    with open(save_path, "wb") as f:
        f.write(graph_image_rawbytes)
    
    print(f"Graph saved as {save_path}")