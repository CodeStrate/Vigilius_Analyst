import streamlit as st
from utils.misc_utils import get_avatar
import pandas as pd, time
from utils.app_utils import (
    clear_cache,
    handle_dataset_upload,
    auto_generate_chart
)

from uuid import uuid4

from utils.ai_providers import list_models_by_provider, list_ollama_models, AVAILABLE_AI_PROVIDERS
from agent.llm_factory import LLMFactory

from agent.agent_handler import SQLAgent
# Page settings
st.set_page_config(
    page_title="Vigilius Analyst App",
    page_icon="📊",
    layout="wide",
)

# Title
st.title("Vigilius Analyst")


# --- Initialize session state ---
if "sql_agent" not in st.session_state:
    st.session_state.sql_agent = None
if "sql_agent_provider" not in st.session_state:
    st.session_state.sql_agent_provider = "openai"
if "sql_agent_model" not in st.session_state:
    st.session_state.sql_agent_model = ""

if "data_assistant" not in st.session_state:
    st.session_state.data_assistant = None
if "data_assistant_provider" not in st.session_state:
    st.session_state.data_assistant_provider = "ollama"
if "data_assistant_model" not in st.session_state:
    st.session_state.data_assistant_model = ""

if "models_configured" not in st.session_state:
    st.session_state.models_configured = False
if "dataset_uploaded" not in st.session_state:
    st.session_state.dataset_uploaded = False
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [] # for showing chats in UI

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid4())

def list_model_options(provider):
    """List available models for the given provider"""
    if provider == "ollama":
        ollama_options = list_ollama_models()
        if ollama_options == []:
            st.warning("No ollama models available, please choose one from https://ollama.com/library")
        return ollama_options
    elif provider in ["openai", "gemini", "groq"]:
        return list_models_by_provider(provider)
    else:
        return []

def create_llm_from_factory():
    """Create LLM instances from the factory"""
    factory = LLMFactory()

    sql_llm = factory.create(
        st.session_state.sql_agent_provider,
        st.session_state.sql_agent_model
    )

    assistant_llm = factory.create(
        st.session_state.data_assistant_provider,
        st.session_state.data_assistant_model
    )

    return sql_llm, assistant_llm

# --- Sidebar ---
st.sidebar.title("⚙️ Configuration")

# File uploader
uploaded_dataset = st.sidebar.file_uploader(
    "Upload a CSV/Excel/SQLite DB file", 
    type=["csv", "xlsx", "db"], 
    key="dataset"
)
if uploaded_dataset is not None and "db_path" not in st.session_state:
    db_path = handle_dataset_upload(uploaded_dataset)
    if db_path:
        st.session_state.db_path = db_path
        st.session_state.dataset_uploaded = True

# Reset button
if st.sidebar.button("🔄 Reset Session"):
    clear_cache()
    st.rerun()

# Model selection
st.sidebar.subheader("🤖 AI Models")

sql_provider = st.sidebar.selectbox(
    "SQL Agent Provider", 
    AVAILABLE_AI_PROVIDERS, 
    index=AVAILABLE_AI_PROVIDERS.index(st.session_state.sql_agent_provider)
)

sql_model_options = sorted(list_model_options(sql_provider))
sql_model = st.sidebar.selectbox(
    "SQL Agent Model", 
    sql_model_options
) if sql_model_options else ""

assistant_provider = st.sidebar.selectbox(
    "Data Assistant Provider", 
    AVAILABLE_AI_PROVIDERS, 
    index=AVAILABLE_AI_PROVIDERS.index(st.session_state.data_assistant_provider)
)

assistant_model_options = sorted(list_model_options(assistant_provider))
assistant_model = st.sidebar.selectbox(
    "Data Assistant Model", 
    assistant_model_options
) if assistant_model_options else ""

# Confirm button applies selections
if st.sidebar.button("✅ Confirm Models"):
    if sql_model and assistant_model:
        with st.spinner("Configuring models..."):
            factory = LLMFactory()
            st.session_state.sql_llm = factory.create(sql_provider, sql_model)
            st.session_state.assistant_llm = factory.create(assistant_provider, assistant_model)

            st.session_state.sql_agent_provider = sql_provider
            st.session_state.sql_agent_model = sql_model
            st.session_state.data_assistant_provider = assistant_provider
            st.session_state.data_assistant_model = assistant_model
            st.session_state.models_configured = True
            st.session_state.sql_agent = None

        st.success("Models configured successfully!")
    else:
        st.error("Please select both SQL Agent and Data Assistant models first.")

with st.sidebar:
    if st.session_state.models_configured:
        st.sidebar.markdown("### 📌 Current Models")
        st.sidebar.markdown(
            f"- **SQL Agent**: `{st.session_state.sql_agent_provider}` → `{st.session_state.sql_agent_model}`"
        )
        st.sidebar.markdown(
            f"- **Data Assistant**: `{st.session_state.data_assistant_provider}` → `{st.session_state.data_assistant_model}`"
        )
# --- Main Chat Container ---
chat_container = st.container()

def main():

    db_path = st.session_state.get("db_path")
    
    # Initialize SQL agent if dataset was uploaded and models are configured
    if (db_path and st.session_state.models_configured and 
        not st.session_state.sql_agent and 
        hasattr(st.session_state, 'sql_llm') and 
        hasattr(st.session_state, 'assistant_llm')):
        
        from agent.data_assistant_handler import DataAssistant
        data_assistant = DataAssistant(st.session_state.assistant_llm)
        st.session_state.sql_agent = SQLAgent(
            db_path=st.session_state.db_path, 
            llm=st.session_state.sql_llm, 
            data_assistant=data_assistant
        ).build_agent()



    with chat_container:
        for message in st.session_state.chat_history:
            with st.chat_message(name=message["sender_type"], avatar=get_avatar(message["sender_type"])):
                if message["message_type"] == "text":
                    st.write(message["content"])
                if message["message_type"] == "dataframe":
                    st.dataframe(message["content"])
                if message["message_type"] == "list":
                    for item in message["content"]:
                        if isinstance(item, pd.DataFrame):
                            st.dataframe(item)
                        else:
                            st.write(item)

    # Chat input
    if (st.session_state.dataset_uploaded and 
        st.session_state.models_configured and 
        st.session_state.sql_agent):
        user_prompt = st.chat_input("How can I assist you with your data...")

        if user_prompt:
            with chat_container:
                with st.chat_message(name="user", avatar=get_avatar("user")):
                    st.markdown(user_prompt)
                    st.session_state.chat_history.append({"sender_type": "user", "message_type": "text", "content": user_prompt})

                with st.chat_message(name="assistant", avatar=get_avatar("assistant")):
                    response_placeholder = st.empty()
                    messages_state = {"messages": [{"role": "user", "content": user_prompt}]}
                    
                     # Just get the response normally first
                    result = st.session_state.sql_agent.invoke(messages_state,
                            config={"configurable" : {"thread_id" : st.session_state.session_id}})
                        
                    # Extract the final response text
                    final_response = ""
                    if result and "messages" in result:
                        final_message = result["messages"][-1]
                        if hasattr(final_message, 'content'):
                            final_response = final_message.content
                        
                    # SIMPLE STREAMING
                    if final_response:
                        try:
                            displayed_text = ""
                            for char in final_response:
                                displayed_text += char
                                response_placeholder.markdown(displayed_text + "▊")  # cursor effect
                                time.sleep(0.02)  # adjust speed as needed
                            # Remove cursor and show final text
                            response_placeholder.markdown(final_response)
                            # Save to chat history
                            st.session_state.chat_history.append({
                                "sender_type": "assistant",
                                "message_type": "text",
                                "content": final_response
                            })
                        except Exception as e:
                            error_msg = f"Sorry, an error occurred: {str(e)}"
                            response_placeholder.markdown(error_msg)
                            st.session_state.chat_history.append({
                                "sender_type": "assistant",
                                "message_type": "text",
                                "content": error_msg
                            })
                    else:
                        response_placeholder.markdown("I couldn't generate a response.")

    else:
        if not st.session_state.dataset_uploaded:
            st.warning("Please upload a dataset first.")
        elif not st.session_state.models_configured:
            st.warning("Please configure your AI models first by clicking 'Confirm Model Selection'.")

if __name__ == "__main__":
    main()
