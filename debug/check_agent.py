from agent.agent_handler import SQLAgent
from agent.data_assistant_handler import DataAssistant
from agent.llm_factory import LLMFactory
factory = LLMFactory()
sql_llm = factory.create("groq", "openai/gpt-oss-120b")
da_llm = factory.create("ollama", "nemotron-mini:latest")

assistant = DataAssistant(llm=da_llm)
agent = SQLAgent(db_path="datasets/complaints_dataset.db", llm=sql_llm, data_assistant=assistant).build_agent()

while True:
    user_input = input("User: ")
    # stream is for graph streaming!!
    for step in agent.stream(
        {"messages" : [{"role" : "user", "content" : user_input}]},
        stream_mode="values",
    ):
        step["messages"][-1].pretty_print()