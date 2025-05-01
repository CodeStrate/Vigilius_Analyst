from openai import OpenAI
import pandas as pd

class OpenAIChatHandler:
    def __init__(self, model_preference: str = "gpt-4o", api_key: str = None):
        self.api_key = api_key
        self.model_preference = model_preference
        self.client = OpenAI(api_key=self.api_key)

    def data_summarizer(self, dataset: pd.DataFrame, schema: str) -> str:
        """Start a new conversation based on uploaded dataset and its schema."""
        try:
            response = self.client.chat.completions.create(
                model=self.model_preference,
                messages = [
                    {"role": "system", "content": "You are a helpful assistant that analyzes datasets."},
                    {"role": "user", "content": f"Here is the table schema:\n{schema}"},
                    {"role": "user", "content": f"""Here is a preview of the dataset:\n{dataset.head(5).to_json()}

                Respond with a short summary of the dataset and its columns.
                     
                Then follow these instructions STRICTLY AS POSSIBLE:
                - Say only 2 lines summarizing the dataset. Don't use values from the dataset that are proper nouns.
                - Don't use bullets or lists for columns, and don't give out data types.
                - Keep the response short and concise.
                - 
                """}
                ],

                temperature=0.3,
                stream=False
            )
            ai_reply = response.choices[0].message.content
            return ai_reply.strip()

        except Exception as e:
            print(f"Error: {e}")
            return "There was an issue starting the conversation. Please try again."

    def get_recommended_queries(self, dataset: pd.DataFrame, schema: str) -> str:
        """Get recommended queries based on the dataset and its schema."""
        try:
            response = self.client.chat.completions.create(
                model=self.model_preference,
                messages = [
                    {"role": "system", "content": "You are an expert data analyst that analyzes datasets, providing recommended queries."},
                    {"role": "user", "content": f"Here is the table schema:\n{schema}"},
                    {"role": "user", "content": f"""Here is a preview of the dataset:\n{dataset.head(5).to_json()}
                     
                Follow these instructions STRICTLY AS POSSIBLE:
                - Say "Here are some recommended queries you can run on this data:"
                - Create a bullet point list (max 3 points) of recommended queries any new user can run on the dataset based on preview.
                - Tailor recommendations to the columns and purpose of dataset. Don't use values from the dataset that are proper nouns.
                - use natural language for the suggested queries.
                - Keep the response short and concise.
                - Only respond with the recommendations — no extra commentary.
                """}
                ],

                temperature=0.3,
                stream=False
            )
            ai_reply = response.choices[0].message.content
            return ai_reply.strip()

        except Exception as e:
            print(f"Error: {e}")
            return "There was an issue getting recommended queries. Please try again."

    def smart_chat(self, user_prompt: str, table_name: str, schema: str, recent_history: list) -> str:
        """Smartly decide whether to clarify or generate SQL based on user input and history."""
        try:
            conversation = [
                {"role": "system", "content": f'''
                    You are a careful but expert Data Analyst helping users analyze and query datasets. \
                    If the user request is ambiguous (missing important details like filters, column names, or conditions), \
                    DO NOT guess. Ask for clarification. \
                    Here is the table name: {table_name}.
                    Here is the table schema:\n{schema}
                    Only generate SQL if you have all the details to confidently write a complete SQL query. \
                    STRICT RULE: If you generate SQL, output only SQL code directly starting with SELECT or WITH, no extra text. \
                    STRICT DISCLAIMER (DO NOT FAIL TO FOLLOW IT): You are writing SQL queries for a SQLite database. 
                    - SQLite does not support TO_DATE, TO_CHAR, EXTRACT.
                    - Dates are usually TEXT fields.
                    - Use SUBSTR() or strftime() functions if you need to extract parts of dates. \
                    
                    If clarifying, just ask a short question.
                    Do not answer questions outside this context.
                '''}
            ]

            for entry in recent_history:
                role = "user" if entry["sender_type"] == "user" else "assistant"
                conversation.append({"role": role, "content": entry["content"]})

            conversation.append({"role": "user", "content": user_prompt})

            response = self.client.chat.completions.create(
                model=self.model_preference,
                messages=conversation,
                temperature=0.3,
                stream=False
            )

            ai_reply = response.choices[0].message.content
            return ai_reply.strip()

        except Exception as e:
            print(f"Error: {e}")
            return "There was an issue processing the request. Please try again."
