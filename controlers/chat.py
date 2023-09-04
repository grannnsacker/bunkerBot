from sqlalchemy.orm import Session

from controlers.setting import create_based_setting
from models import Game, Chat
from store import postgresDB


def get_chat_by_telegram_id(chat_id: str, session: Session):
    chat = session.query(Chat).filter_by(chat_telegram_id=chat_id).first()
    return chat


def register_chat(chat_telegram_id: str, chat_name: str, session: Session):
    setting = create_based_setting(session)
    chat = Chat(chat_telegram_id=chat_telegram_id, chat_name=chat_name, settings_id=setting.id, settings=setting)
    session.add(chat)
    return True


