from sqlalchemy.orm import Session

from controlers.game import get_game_by_chat_id
from controlers.setting import create_based_setting
from models import Setting, User


def register_user(username: str, user_id: str, session: Session):
    setting = create_based_setting(session)
    user = User(username=username, user_id=user_id, settings_id=setting.id, settings=setting)
    session.add(user)


def get_user_by_user_id(user_id: str, session: Session):
    player = session.query(User).filter_by(user_id=user_id).order_by(User.id.desc()).first()
    return player
