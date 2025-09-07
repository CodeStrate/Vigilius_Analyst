from agent.agent_handler import SQLAgent

agent = SQLAgent().build_agent()

while True:
    user_input = input("User: ")
    # stream is for graph streaming!!
    for step in agent.stream(
        {"messages" : [{"role" : "user", "content" : user_input}]},
        stream_mode="values",
    ):
        step["messages"][-1].pretty_print()