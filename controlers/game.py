import datetime

from sqlalchemy.orm import Session
from sqlalchemy.orm.collections import InstrumentedList

from models import Game, Player
from store import postgresDB


def create_game(chat_id: str, start_message_id: str, size: str, time_spent:str, disaster:str,
                condition: str, build_reason: str, location: str, room_1: str, room_2: str,
                room_3: str, available_resource_1: str, available_resource_2: str, session: Session):
    game = Game(chat_id=chat_id, start_message_id=start_message_id, start_time=datetime.datetime.now(),
                size=size, time_spent=time_spent, disaster=disaster, condition=condition,
                build_reason=build_reason, location=location, room_1=room_1, room_2=room_2,
                room_3=room_3, available_resource_1=available_resource_1,
                available_resource_2=available_resource_2)
    session.add(game)


def stop_game(chat_id: str, session: Session):
    game = get_game_by_chat_id(chat_id, session)
    game.end_time = datetime.datetime.now()


def get_game_by_chat_id(chat_id: str, session: Session):
    game = session.query(Game).filter_by(chat_id=chat_id).order_by(Game.id.desc()).first()
    return game


def get_players_usernames_by_chat_id(chat_id: str, session: Session):
    players_ = [i.username for i in get_game_by_chat_id(chat_id, session).players]
    return players_


def get_players_id_by_chat_id(chat_id: str, session: Session):
    players_ = [i.user_id for i in get_game_by_chat_id(chat_id, session).players]
    return players_


def get_alive_players_id_by_chat_id(chat_id: str, session: Session):
    players_ = [i.user_id for i in get_game_by_chat_id(chat_id, session).players if not i.is_dead]
    return players_


def get_need_for_rekick_players_id_by_chat_id(chat_id: str, session: Session):
    players_ = [i.user_id for i in get_game_by_chat_id(chat_id, session).players if i.is_need_to_be_in_rekick_vote]
    return players_


def get_message_id_by_chat_id(chat_id: str, session: Session):
    msg_id = session.query(Game).filter_by(chat_id=chat_id).order_by(Game.id.desc()).first().start_message_id
    return msg_id


def get_turn_by_chat_id(chat_id: str, session: Session):
    game = get_game_by_chat_id(chat_id, session)
    turn = game.turn
    return turn



#def get_game_by_id(game_id: int, session: Session):
#    game = session.query(Game).filter_by(game_id=game_id).order_by(Game.id.desc()).first()







