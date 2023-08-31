from sqlalchemy.orm import Session

from models import Game, Player
from store import postgresDB


def get_player_by_user_id(user_id: str, session: Session):
    player = session.query(Player).filter_by(user_id=user_id).order_by(Player.id.desc()).first()
    return player


def get_count_of_open_params(user_id: str, session: Session):
    player = get_player_by_user_id(user_id, session)
    cnt = 0
    if player.is_sex_open:
        cnt += 1
    if player.is_hobby_open:
        cnt += 1
    if player.is_luggage_open:
        cnt += 1
    if player.is_fear_open:
        cnt += 1
    if player.is_personality_open:
        cnt += 1
    if player.is_add_inf_open:
        cnt += 1
    if player.is_health_open:
        cnt += 1
    if player.is_knowledge_open:
        cnt += 1
    return cnt


def get_game_by_person_msg_id(person_msg_id: str, session: Session):
    player = session.query(Player).filter_by(person_msg_id=person_msg_id).order_by(Player.id.desc()).first()
    return player.game