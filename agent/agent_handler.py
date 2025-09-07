from langchain_core.messages import AIMessage
from typing import List, Literal
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode
from agent.data_assistant_handler import respond, validate_intent

from uuid import uuid4
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.utilities import SQLDatabase
from langchain_openai import ChatOpenAI
from utils.app_utils import get_db_and_dialect
# from utils.misc_utils import get_chinook_db_and_dialect
from utils.misc_utils import get_last_user_message
from agent.prompts import GENERATE_SQL_QUERY_PROMPT, CHECK_SQL_QUERY_PROMPT

class SQLAgentHandler:

    def __init__(self, db: SQLDatabase, dialect: str = "sqlite", model_name: str = "gpt-4o", temperature: float = 0.5, top_k: int = 10):
        self.llm = ChatOpenAI(model=model_name, temperature=temperature)
        self.top_k = top_k
        self.db = db
        self.dialect = dialect
        
        # this has all the tools we need prebuilt
        self.toolkit = SQLDatabaseToolkit(db=self.db, llm=self.llm)
        self.tools = self.toolkit.get_tools()
    
        ### We have the following tools:
        # sql_db_query
        # sql_db_schema
        # sql_db_list_tables
        # sql_db_query_checker
        # ----------------------------------------
    
    # 0. get individual tools
    def get_individual_tools(self):
        """
        Returns a dictionary mapping tool names to tool objects for easy access.
        """
        return {tool.name: tool for tool in self.tools}

    def bind_tool_and_invoke(self, tool_names, messages, tool_choice : str = None):
        tools = [self.get_individual_tools()[name] for name in tool_names]
        llm = self.llm.bind_tools(tools, tool_choice=tool_choice)
        return llm.invoke(messages)

    # 1. make a predetermined tool call
    def list_sql_tables(self, state: MessagesState):
        """
        Make a list tables tool call ourselves first.
        """
        tool_call = {
            "name" : "sql_db_list_tables",
            "args" : {},
            "id" : str(uuid4()), # any unique str works if you want
            "type" : "tool_call"
        }

        tool_call_message = AIMessage(content="", tool_calls=[tool_call])
        list_sql_tables_tool = self.get_individual_tools()["sql_db_list_tables"]

        tool_message = list_sql_tables_tool.invoke(tool_call)
        response = AIMessage(f"Available Tables: {tool_message.content}")

        return {"messages" : [tool_call_message, tool_message, response]}

    # 2. force a tool call
    def call_get_schema(self, state: MessagesState):
        """
        Force LLM to call db_schema tool.
        """
        response = self.bind_tool_and_invoke(["sql_db_schema"],state["messages"], tool_choice="any")

        return {"messages" : [response]}

    # 3. Now we dont have to force any tool call
    def generate_query(self, state: MessagesState):
        """
        Use this to generate an SQL query using sql_db_query tool.
        """
        system_message = {
            "role" : "system",
            "content" : GENERATE_SQL_QUERY_PROMPT.format(dialect=self.dialect, top_k=self.top_k)
        }

        response = self.bind_tool_and_invoke(["sql_db_query"], [system_message] + state["messages"])

        return {"messages" : [response]}

    def check_query(self, state: MessagesState):
        """
        Generate a user message with an SQL query and a checker prompt to validate query.
        """
        system_message = {
            "role" : "system",
            "content" : CHECK_SQL_QUERY_PROMPT.format(dialect=self.dialect)
        }
        # generate a user message with sql query to invoke the checker tool
        user_sql_query = ""
        messages = state["messages"]
        for msg in reversed(messages):
            if hasattr(msg, 'tool_calls') and msg.tool_calls:
                user_sql_query = msg.tool_calls[0]["args"]["query"]
                break
            
        user_message = {
            "role" : "user",
            "content" : user_sql_query
        }

        response = self.bind_tool_and_invoke(["sql_db_query"], [system_message, user_message], tool_choice="any")

        return {"messages" : [response]}

    # get tool nodes for schema and query
    def get_schema_and_query_tool_nodes(self) -> List[ToolNode]:
        get_schema_tool = self.get_individual_tools()["sql_db_schema"]
        get_schema_node = ToolNode([get_schema_tool], name="get_schema")
        run_query_tool = self.get_individual_tools()["sql_db_query"] 
        run_query_node = ToolNode([run_query_tool], name="run_query")
        return [get_schema_node, run_query_node]

    def intent_classify(self, state: MessagesState):
        user_message = get_last_user_message(state["messages"])
        raw_intent = respond(user_message, do_intent=True)
        intent_validation = validate_intent(raw_intent)

        intent_message = AIMessage(content=f'Intent classified as {intent_validation}')
        return {"messages" : [intent_message]}

    def handle_small_talk(self, state: MessagesState):
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
    def route_after_intent(self, state: MessagesState) -> Literal["list_sql_tables", "handle_small_talk"]:
        last_message = state["messages"][-1]

        if "sql_query" in last_message.content:
            return "list_sql_tables"
        elif "small_talk" in last_message.content:
            return "handle_small_talk"
        else:
            return "handle_small_talk"

    # conditional in graph
    def should_continue_query(self, state:MessagesState) -> str | None:
        last_message = state["messages"][-1]

        if not last_message.tool_calls:
            return END
        elif last_message.tool_calls[0]["name"] == "sql_db_query":
            return "run_query"
        else:
            return "check_query"

class SQLAgent:
    def __init__(self, db_path: str):
        self.db, self.dialect = get_db_and_dialect(db_path=db_path)
        self.handler = SQLAgentHandler(db=self.db, dialect=self.dialect)

    def build_agent(self):
        tool_nodes = self.handler.get_schema_and_query_tool_nodes()
        builder = StateGraph(MessagesState)

        # add nodes for intent and small talk
        builder.add_node(self.handler.intent_classify)
        builder.add_node(self.handler.handle_small_talk)

        # add nodes
        builder.add_node(self.handler.list_sql_tables)
        builder.add_node(self.handler.call_get_schema)
        builder.add_node(tool_nodes[0], "get_schema")
        builder.add_node(self.handler.generate_query)
        builder.add_node(self.handler.check_query)
        builder.add_node(tool_nodes[1], "run_query")

        # add edges
        builder.add_edge(START, "intent_classify")

        builder.add_conditional_edges(
            "intent_classify",
            self.handler.route_after_intent,
        )

        # end small talk
        builder.add_edge("handle_small_talk", END)

        builder.add_edge("list_sql_tables", "call_get_schema")
        builder.add_edge("call_get_schema", "get_schema")
        builder.add_edge("get_schema", "generate_query")

        # add conditional edge
        builder.add_conditional_edges(
            "generate_query",
            self.handler.should_continue_query,
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

    def save_agent_graph(self, save_path="agent_graph.png"):
        graph_image_rawbytes = self.agent.get_graph().draw_mermaid_png()

        with open(save_path, "wb") as f:
            f.write(graph_image_rawbytes)
        
        print(f"Graph saved as {save_path}")