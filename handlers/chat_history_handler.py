from sqlalchemy import create_engine, Column, Integer, String, Text, LargeBinary, desc
from sqlalchemy.orm import sessionmaker, declarative_base, scoped_session
from utils.utils import load_config
import os

config = load_config()
Base = declarative_base()

class ChatHistory(Base):
    __tablename__ = "chat_history"

    message_id = Column(Integer, primary_key=True, autoincrement=True)
    chat_history_id = Column(String, nullable=False)    
    sender_type = Column(String, nullable=False)       
    message_type = Column(String, nullable=False)       
    text_content = Column(Text, nullable=True)           
    blob_content = Column(LargeBinary, nullable=True)    

class ChatHistoryManager:

    def __init__(self, db_path=config["chat_sessions_database_path"]):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_url = f"sqlite:///{db_path}"

        self.engine = create_engine(self.db_url, connect_args={"check_same_thread": False})
        self._session_factory = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.session = scoped_session(self._session_factory)

        Base.metadata.create_all(self.engine)


    def save_text_message(self, chat_history_id, sender_type, text_content):
        session = self.session()
        try:
            new_message = ChatHistory(
                chat_history_id=chat_history_id,
                sender_type=sender_type,
                message_type="text",
                text_content=text_content,
                blob_content=None
            )
            session.add(new_message)
            session.commit()
        finally:
            session.close()

    def save_audio_message(self, chat_history_id, sender_type, blob_content):
        session = self.session()
        try:
            new_message = ChatHistory(
                chat_history_id=chat_history_id,
                sender_type=sender_type,
                message_type="audio",
                text_content=None,
                blob_content=blob_content
            )
            session.add(new_message)
            session.commit()

        finally:
            session.close()

    def get_all_chat_history_list(self):
        session = self.session()
        try:
            messages = session.query(ChatHistory).order_by(ChatHistory.chat_history_id).all()
            chat_history_id_list = [message.chat_history_id for message in messages]
            return chat_history_id_list
        finally:
            session.close()
    
    def load_chat_history(self, chat_history_id):
        session = self.session()
        try:
            messages = session.query(ChatHistory).filter(ChatHistory.chat_history_id == chat_history_id).order_by(ChatHistory.message_id).all()
            return messages
        finally:
            session.close()

    def delete_chat_history(self, chat_history_id):
        session = self.session()
        try:
            session.query(ChatHistory).filter(ChatHistory.chat_history_id == chat_history_id).delete()
            session.commit()

        finally:
            session.close()