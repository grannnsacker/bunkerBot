from sqlalchemy import Column, BigInteger, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import relationship

from store import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String)
    user_id = Column(String)  # Telegram user id
    settings_id = Column(Integer, ForeignKey('settings.id'), index=True)
    diamonds = Column(Integer, default=0)
    money = Column(Integer, default=0)
    settings = relationship("Setting", back_populates="user")
