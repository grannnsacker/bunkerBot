from sqlalchemy import Column, BigInteger, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import relationship

from store import Base


class Game(Base):
    __tablename__ = "games"
    id = Column(Integer, primary_key=True)
    chat_id = Column(String, nullable=False)
    turn = Column(Integer, default=0)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    chat_name = Column(String)
    start_message_id = Column(String)
    invite_link_to_chat = Column(String)
    final_vote_msg_id = Column(String)
    likes = Column(Integer, default=0)
    dislikes = Column(Integer, default=0)
    '''disaster'''
    disaster = Column(String)

    '''bunker params'''
    size = Column(String)  # shelter size m^2
    time_spent = Column(String)
    condition = Column(String)  # expm: полузаброшенный бункер, в котором часто мигает свет
    build_reason = Column(String)  # expm: изначально построен для укрытия президента
    location = Column(String)  # expm: побережье Черного моря
    room_1 = Column(String)  # expm: оранжерея (состояние неизвестно)
    room_2 = Column(String)  # expm: оружейная (в идеальном состоянии)
    room_3 = Column(String)  # expm: медицинский кабинет (дверь заблокирована)
    available_resource_1 = Column(String)  # expm: консервы тушёнки
    available_resource_2 = Column(String)  # expm: 5 новых ноутбуков
    '''# expm: Из-а случайно созданного учёными вируса, поражающео исключительно людей,
     половина человечества превратилась в опасных хищников.'''
    players = relationship("Player", back_populates="game")