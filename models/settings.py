from sqlalchemy import Column, BigInteger, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import relationship

from store import Base


class Setting(Base):
    __tablename__ = "settings"
    id = Column(Integer, primary_key=True)
    user = relationship("User", back_populates="settings")
    max_players_in_shelter = Column(Integer, default=2)  # max_pla // 2 # how many people
    privileges_is_available = Column(Boolean, default=True)
    max_players = Column(Integer, default=10)

    '''cards'''
    exchange_add = Column(Boolean, default=True)
