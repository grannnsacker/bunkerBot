from sqlalchemy import Column, BigInteger, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import relationship

from store import Base


class Chat(Base):
    __tablename__ = "chats"
    id = Column(Integer, primary_key=True)
    chat_name = Column(String)
    chat_telegram_id = Column(String)  # Telegram user id
    settings_id = Column(Integer, ForeignKey('settings.id'), index=True)
    settings = relationship("Setting", back_populates="chat")
    premium = Column(Boolean, default=False)
