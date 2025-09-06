from sqlalchemy import create_engine
import pandas as pd
import time, os
import tempfile
import streamlit as st
from utils.misc_utils import get_dataframe, get_timestamp
import plotly.express as px

# --- Utility Functions ---
def get_session_key():
    if "session_key" not in st.session_state or st.session_state.session_key == "new_session":
        st.session_state.session_key = get_timestamp()
    return st.session_state.session_key

def clear_cache():
    st.cache_resource.clear()
    st.session_state.clear()


def save_dataframe_to_sqlite(df, table_name, db_path):
    """Save DataFrame to SQLite."""
    engine = create_engine(f"sqlite:///{db_path}")
    df.to_sql(table_name, engine, if_exists='replace', index=False)

def handle_dataset_upload(uploaded_dataset):
    if uploaded_dataset is not None and not st.session_state.dataset_uploaded:
        with st.spinner("Processing your dataset..."):
            time.sleep(1)  # Simulate processing time
            dataset = get_dataframe(uploaded_dataset)
            table_name = "uploaded_dataset"
            db_path = "./datasets/uploaded_dataset.db"

            os.makedirs(os.path.dirname(db_path), exist_ok=True)

            save_dataframe_to_sqlite(dataset, table_name, db_path)
            
def auto_generate_chart(df: pd.DataFrame):
    """Auto-generate a bar chart based on DataFrame structure."""
    try:
        if df.empty or df.shape[1] < 1:
            st.warning("DataFrame is empty or lacks sufficient columns.")
            return

        col1 = df.columns[0]
        col2 = df.columns[1] if df.shape[1] > 1 else None

        if col2 is None:
            # Single column: count occurrences
            chart_data = df[col1].value_counts().reset_index()
            chart_data.columns = [col1, "count"]
            x_col, y_col = col1, "count"

        elif pd.api.types.is_numeric_dtype(df[col2]):
            # One categorical, one numeric: group and sum
            chart_data = df.groupby(col1)[col2].sum().reset_index()
            x_col, y_col = col1, col2

        else:
            # Both categorical: count combinations
            chart_data = df.groupby([col1, col2]).size().reset_index(name='count')
            x_col, y_col = col1, "count"
            fig = px.bar(
                chart_data,
                x=x_col,
                y=y_col,
                color=col2,
                barmode="group",
                title=f"Bar Chart: {col1} and {col2}",
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            st.plotly_chart(fig, use_container_width=True)
            return

        # Simple bar chart
        fig = px.bar(
            chart_data,
            x=x_col,
            y=y_col,
            color=x_col,
            title=f"Bar Chart: {y_col} by {x_col}",
            color_discrete_sequence=px.colors.qualitative.Vivid
        )
        fig.update_layout(margin=dict(t=60, b=40))
        st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"Chart generation failed: {e}")
        st.exception(e)
# def transcribe_audio_recording(voice_recording):
#     if isinstance(voice_recording, dict) and "bytes" in voice_recording:
#         with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_audio_file:
#             temp_audio_file.write(voice_recording["bytes"])
#             wav_file_path = temp_audio_file.name
#         transcribed_text = st.session_state.stt_handler.transcribe_audio(wav_file_path)
#         return transcribed_text if transcribed_text else "Transcription failed."
#     return None