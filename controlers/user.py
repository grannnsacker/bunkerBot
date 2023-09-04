from sqlalchemy.orm import Session

from controlers.game import get_game_by_chat_id
from controlers.setting import create_based_setting
from models import Setting, User


def register_user(username: str, user_id: str, session: Session):
    user = User(username=username, user_id=user_id)
    session.add(user)


def get_user_by_user_id(user_id: str, session: Session):
    user = session.query(User).filter_by(user_id=user_id).first()
    return user


def get_user_by_id(id: int, session: Session):
    user = session.query(User).filter_by(id=id).first()
    return user
