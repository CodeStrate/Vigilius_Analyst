import streamlit as st
from utils.misc_utils import get_avatar
import pandas as pd, time, io
from utils.misc_utils import load_config
from utils.app_utils import (
    clear_cache,
    handle_dataset_upload,
    auto_generate_chart
)

config = load_config()

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
if "dataset_uploaded" not in st.session_state:
    st.session_state.dataset_uploaded = False
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- Sidebar ---
with st.sidebar.expander("Sidebar", expanded=True):
    uploaded_dataset = st.file_uploader("Upload a CSV or Excel file", type=["csv", "xlsx"], key="dataset")
    reset_session = st.button("Reset chat session", key="reset_session")
    if reset_session:
        clear_cache()
        st.rerun()

# --- Main Chat Container ---
chat_container = st.container()


def main():
    db_path = handle_dataset_upload(uploaded_dataset)  # Get the db_path from upload
    
    # Initialize SQL agent if dataset was uploaded
    if db_path and not st.session_state.sql_agent:
        st.session_state.sql_agent = SQLAgent(db_path=db_path).build_agent()

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
    if st.session_state.dataset_uploaded and st.session_state.sql_agent:
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
                    result = st.session_state.sql_agent.invoke(messages_state)
                        
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
        st.warning("Please upload a dataset first to start chatting.")

if __name__ == "__main__":
    main()
