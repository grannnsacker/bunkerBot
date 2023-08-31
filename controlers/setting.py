from sqlalchemy.orm import Session

from controlers.game import get_game_by_chat_id
from models import Game, Setting


def create_based_setting(session: Session):
    setting = Setting()
    session.add(setting)
    return setting


def get_settings_by_id(settings_id: str, session: Session):
    setting_obj = session.query(Setting).filter_by(id=settings_id).first()
    return setting_obj


def get_max_player_chat_id(chat_id: str, session: Session):
    game = get_game_by_chat_id(chat_id, session)
    setting_obj = get_settings_by_id(game.settings_id, session)
    return setting_obj.max_players