import streamlit as st
import pandas as pd
from typing import List
from langchain_community.utilities import SQLDatabase


def get_last_user_message(messages: List) -> str:
    for msg in reversed(messages):
        # Langchain format
        if hasattr(msg, 'type') and msg.type == 'human':
            return msg.content
        elif isinstance(msg, dict) and msg.get('role') == 'user':
            return msg.get('content', '')
        elif hasattr(msg, 'role') and getattr(msg, 'role') == 'user':
            return msg.get('content', '')
        
    # fallback
    return "Hello"

def get_chinook_db_and_dialect(db_path: str = "Chinook.db"):
    db = SQLDatabase.from_uri(f"sqlite:///{db_path}")
    return db, db.dialect

def get_avatar(sender_type):
    if sender_type == "user":
        return "assets/chat_icons/user_image.png"
    else:
       return "assets/chat_icons/bot_image.png"
    
    
def get_dataframe(uploaded_file):
    file_types = {
        "csv": pd.read_csv,
        "xlsx": pd.read_excel
    }
    if uploaded_file is not None:
        file_extension = uploaded_file.name.split(".")[-1]
        if file_extension in file_types:
            return file_types[file_extension](uploaded_file)
        else:
            st.error("Unsupported file type. Please upload a CSV or Excel file.")