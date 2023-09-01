import datetime

from aiogram import types

from controlers.game import get_game_by_chat_id, \
    get_players_usernames_by_chat_id, get_message_id_by_chat_id, get_players_id_by_chat_id, get_turn_by_chat_id
from controlers.player import get_player_by_user_id
from controlers.setting import get_settings_by_id
from controlers.user import get_user_by_user_id, register_user, get_user_by_id
from create_bot import bot
from generation.generate import generate_person
from models import Player
from store import postgresDB

from handlers.callback_query_handlers import round
from text.text_returner import get_profile_text, get_me_text, get_apocalypses_and_bunker_text


async def command_start(message: types.Message):
    session = postgresDB.get_session()
    if get_user_by_user_id(str(message.from_user.id), session) is None:
        register_user(message.from_user.username, message.from_user.id, session)
        session.commit()
    if message.chat.type == "private":
        if len(message.text.split()) > 1:
            chat_id = message.text.split()[1]
            game = get_game_by_chat_id(chat_id, session)
            if len(game.players) + 1 <= get_user_by_id(game.host_id, session).settings.max_players \
                    and message.from_user.username not in get_players_usernames_by_chat_id(chat_id, session):
                game_person = generate_person()
                game.players.append(
                    Player(user_id=message.from_user.id, game_id=chat_id, username=message.from_user.username,
                           personality=game_person["personality"], age=game_person["age"], job=game_person["job"],
                           sex=game_person["sex"], hobby=game_person["hobby"], fear=game_person["fear"],
                           luggage=game_person["luggage"], health=game_person["health"],
                           knowledge=game_person["knowledge"],
                           add_inf=game_person["add_inf"], card_1=game_person["card_action"],
                           card_2=game_person["card_2"]))
                session.add(game)
                n = '\n'
                await bot.edit_message_text(message_id=get_message_id_by_chat_id(chat_id, session),
                                            text=f"Сейчас в игре:\n{f'{n}'.join(get_players_usernames_by_chat_id(chat_id, session))}",
                                            chat_id=chat_id)

            elif message.from_user.username in get_players_usernames_by_chat_id(chat_id, session):
                await message.answer(text="Вы уже в игре")
            else:
                await message.answer(text="В игре нет места")

        elif message.chat.type == "private":
            buttons = [
                types.InlineKeyboardButton(text="Добавить в группу", url="https://t.me/SllizBot?startgroup=start"),
                types.InlineKeyboardButton(text="Войти в чат", callback_data="1"),
                types.InlineKeyboardButton(text="Новости", callback_data="2"),
                types.InlineKeyboardButton(text="Помощь", callback_data="3"),
            ]
            keyboard = types.InlineKeyboardMarkup(row_width=1)
            keyboard.add(*buttons)
            await message.answer(text="Привет я бот-попуск", reply_markup=keyboard)
    else:
        game = get_game_by_chat_id(str(message.chat.id), session)

        if game and game.start_time < datetime.datetime.now() and game.end_time is None:
            await message.answer(text="В вышем чате уже идет игра")
        else:

            buttons = [
                types.InlineKeyboardButton(text="Начать игру",
                                           callback_data=f"start_game!{get_user_by_user_id(str(message.from_user.id), session).id}")
            ]
            keyboard = types.InlineKeyboardMarkup(row_width=1)
            keyboard.add(*buttons)

            await message.answer(text="Привет, сыграем?", reply_markup=keyboard) # message.chat.id
    session.commit()
    session.close()


async def command_me(message: types.Message):
    session = postgresDB.get_session()
    player = get_player_by_user_id(str(message.from_user.id), session)
    if player.game and player.game.start_time < datetime.datetime.now() and player.game.end_time is None:
        buttons = [types.InlineKeyboardButton(text="Апокалипсис", callback_data="change_person_msg_to_apocalypse"),
            types.InlineKeyboardButton(text="Бункер", callback_data="change_person_msg_to_shelter")]
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        keyboard.add(*buttons)
        res = await bot.send_message(chat_id=player.user_id, text=get_me_text(player), parse_mode="HTML",
                               reply_markup=keyboard)
        player.person_msg_id = res.message_id
        session.add(player)
    session.commit()
    session.close()


async def command_go(message: types.Message):
    '''закончить регестрация и начать игру'''
    session = postgresDB.get_session()
    game = get_game_by_chat_id(str(message.chat.id), session)
    if get_turn_by_chat_id(str(message.chat.id), session) == 0:
        await bot.send_message(chat_id=str(message.chat.id),
                               text=get_apocalypses_and_bunker_text(game), parse_mode="HTML")
        buttons = [types.InlineKeyboardButton(text="Апокалипсис", callback_data="change_person_msg_to_apocalypse"),
                types.InlineKeyboardButton(text="Бункер", callback_data="change_person_msg_to_shelter")]
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        keyboard.add(*buttons)
        for id in get_players_id_by_chat_id(str(message.chat.id), session):
            player = get_player_by_user_id(id, session)
            res = await bot.send_message(chat_id=str(id),
                                         text=get_me_text(player),
                                         reply_markup=keyboard,
                                         parse_mode="HTML")   # здесь потом измениить карточку за денежку
            player.person_msg_id = res.message_id
            session.add(player)
        session.commit()
        session.close()
        await round(str(message.chat.id))
    session.commit()
    session.close()


async def cancel_game(message: types.Message):
    '''Принудительное завершение игры'''
    session = postgresDB.get_session()
    if message.chat.type != "private":
        game = get_game_by_chat_id(str(message.chat.id), session)
        if game and game.start_time < datetime.datetime.now() and game.end_time is None:
            game.end_time = datetime.datetime.now()
            await bot.send_message(chat_id=message.chat.id, text="Игра была принудительно завершена")
            session.add(game)
            session.commit()
    session.close()


async def command_card(message: types.Message):
    '''Команда открытия карточки'''
    await bot.delete_message(message_id=message.message_id, chat_id=message.chat.id)
    session = postgresDB.get_session()
    player = get_player_by_user_id(message.from_user.id, session)
    if player and not player.is_card_1_open:
        card_type, card_text = player.card_1.split("!")
        buttons = [types.InlineKeyboardButton(text="Активировать карточку", callback_data=f"activate_action_card!{card_type}"),
                   types.InlineKeyboardButton(text="Закрыть панель", callback_data="close_card_panel")]
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        keyboard.add(*buttons)
        res = await bot.send_message(chat_id=message.from_user.id, text=f"<b>{card_text}</b>",
                                     reply_markup=keyboard,  # сделать чтобы первая буква была большой
                                     parse_mode="HTML")
        player.card_msg_id = res.message_id
        session.add(player)
        session.commit()

    session.close()


async def command_profile(message: types.Message):
    session = postgresDB.get_session()
    text_ = get_profile_text(get_user_by_user_id(str(message.from_user.id), session))
    await bot.send_message(chat_id=message.from_user.id,
                           text=text_,
                           parse_mode="HTML")

    session.close()
