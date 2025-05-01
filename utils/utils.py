import os, yaml
import requests
import streamlit as st
import pandas as pd
from dotenv import load_dotenv
load_dotenv()

def load_config():
    with open("config.yaml", "r") as f:
        return yaml.safe_load(f)

def list_openai_models():
    openai_api_key = os.getenv("OPENAI_API_KEY")
    response = requests.get("https://api.openai.com/v1/models", headers={"Authorization": f"Bearer {openai_api_key}"}).json()
    if response.get("error", False):
        st.warning("Openai Error: " + response["error"]["message"])
        return []
    else:
        return [item["id"] for item in response["data"]]
    
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

def get_timestamp():
    return pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")