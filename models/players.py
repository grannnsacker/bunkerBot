from sqlalchemy import Column, BigInteger, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import relationship

from store import Base


class Player(Base):
    __tablename__ = "players"
    id = Column(Integer, primary_key=True)
    game_id = Column(Integer, ForeignKey('games.id'), index=True)
    user_id = Column(String) # Telegram user id
    username = Column(String)
    msg_id = Column(String)  # field to save message id in cur private chat
    person_msg_id = Column(String)  # field to save message id, which will be swap me->apocalypses->shelter
    card_msg_id = Column(String)  # field to save card message id, which will be delete
    voices_to_kick = Column(Integer, default=0)
    is_vote = Column(Boolean, default=False)
    is_dead = Column(Boolean, default=False)
    is_need_to_be_in_rekick_vote = Column(Boolean, default=False)
    job = Column(String)
    is_job_open = Column(Boolean, default=False)
    sex = Column(String)
    is_sex_open = Column(Boolean, default=False)
    age = Column(Integer)
    is_age_open = Column(Boolean, default=False)
    hobby = Column(String)
    is_hobby_open = Column(Boolean, default=False)
    personality = Column(String)
    is_personality_open = Column(Boolean, default=False)
    fear = Column(String)
    is_fear_open = Column(Boolean, default=False)
    luggage = Column(String)
    is_luggage_open = Column(Boolean, default=False)
    health = Column(String)
    is_health_open = Column(Boolean, default=False)
    add_inf = Column(String)
    is_add_inf_open = Column(Boolean, default=False)
    knowledge = Column(String)
    is_knowledge_open = Column(Boolean, default=False)
    card_1 = Column(String)
    is_card_1_open = Column(Boolean, default=False)
    card_2 = Column(String)
    is_card_2_open = Column(Boolean, default=False)

    game = relationship("Game", back_populates="players")
