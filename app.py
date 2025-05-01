import streamlit as st
from streamlit_mic_recorder import mic_recorder
from utils.utils import get_avatar, load_config
from handlers.chat_handler import OpenAIChatHandler
from handlers.stt_handler import OpenAISpeechHandler
import os, pandas as pd, time, random
from dotenv import load_dotenv
from utils.app_utils import (
    clear_cache,
    handle_dataset_upload,
    get_table_schema_sqlalchemy,
    extract_sql_code,
    transcribe_audio_recording,
    execute_sql_query,
    auto_generate_chart
)

config = load_config()

# Load environment
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

# Page settings
st.set_page_config(
    page_title="Chatbot App",
    page_icon="🤖",
    layout="wide",
)

# Title
st.title("Chatbot App 🤖")

def artificial_delay(seconds=3.0):
    placeholder = st.empty()
    delay_interval = 0.1  # Smaller step gives smoother feel
    steps = int(seconds / delay_interval)
    
    for i in range(steps):
        dots = "." * ((i % 3) + 1)
        placeholder.markdown(f"Thinking{dots}")
        time.sleep(delay_interval)
    
    placeholder.empty()  # Clear after delay

# --- Initialize session state ---
if "chat_handler" not in st.session_state:
    st.session_state.chat_handler = OpenAIChatHandler(api_key=openai_api_key)
if "stt_handler" not in st.session_state:
    st.session_state.stt_handler = OpenAISpeechHandler(api_key=openai_api_key)
if "dataset_uploaded" not in st.session_state:
    st.session_state.dataset_uploaded = False
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "query_results" not in st.session_state:
    st.session_state.query_results = []

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
    handle_dataset_upload(uploaded_dataset)  # Ensure this processes the file and updates session state

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

    # Chat + Mic input together
    if st.session_state.dataset_uploaded and st.session_state.chat_handler:
        # Layout for input + mic
        col1, col2 = st.columns([20, 1])  # Bigger for text input, smaller for mic

        with col1:
            user_prompt = st.chat_input("How can I assist you with your data...")

        with col2:
            voice_recording = mic_recorder(
                start_prompt="🎙️",
                stop_prompt="⏹️",
                just_once=True,
                use_container_width=True,
                key="mic_recorder_inline"
            )

        # Priority: If voice was recorded, prefer that over text
        if voice_recording and "bytes" in voice_recording:
            user_prompt = transcribe_audio_recording(voice_recording)

        if user_prompt:
            with chat_container:
                dataset = config["uploaded_dataset_path"]
                table_name = config["table_name"]
                with st.chat_message(name="user", avatar=get_avatar("user")):
                    st.markdown(user_prompt)
                    st.session_state.chat_history.append({"sender_type": "user", "message_type": "text", "content": user_prompt})

                with st.chat_message(name="assistant", avatar=get_avatar("assistant")):
                    schema = get_table_schema_sqlalchemy(dataset, table_name)
                    recent_history = st.session_state.query_results[-8:]

                    with st.spinner("Please wait..."):
                        artificial_delay(random.uniform(2.0, 4.0))  # artificial delay
                        ai_response = st.session_state.chat_handler.smart_chat(user_prompt, table_name, schema, recent_history)
                    
                        sql_query = extract_sql_code(ai_response)

                        if sql_query:
                            query_execution = execute_sql_query(sql_query, dataset)
                            if query_execution is not None:
                                if isinstance(query_execution, pd.DataFrame):
                                    st.dataframe(query_execution)
                                    # Only generate chart if DataFrame is large enough
                                    if query_execution.shape[1] >= 2 and query_execution.shape[0] >= 2:
                                        st.info("Generated chart...")
                                        auto_generate_chart(query_execution)  # Chart will be auto-generated here
                                    st.session_state.chat_history.append({"sender_type": "assistant", "message_type": "dataframe", "content": query_execution})
                                else:
                                    st.info(query_execution)
                                    st.session_state.chat_history.append({"sender_type": "assistant", "message_type": "text", "content": query_execution})
                            else:
                                st.error("No results found or error executing query.")
                        else:
                            st.markdown(ai_response)
                            st.session_state.chat_history.append({"sender_type": "assistant", "message_type": "text", "content": ai_response})

            # Update session history
            st.session_state.query_results.append({"sender_type": "user", "message_type": "text", "content": user_prompt})
            st.session_state.query_results.append({"sender_type": "assistant", "message_type": "text", "content": ai_response})

    else:
        st.warning("Please upload a dataset first to start chatting.")

if __name__ == "__main__":
    main()
