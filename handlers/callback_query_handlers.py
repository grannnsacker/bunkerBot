import aiogram.utils.exceptions
from aiogram.utils.exceptions import MessageNotModified, MessageToEditNotFound

from controlers.chat import get_chat_by_telegram_id
from controlers.game import create_game, get_alive_players_id_by_chat_id, get_message_id_by_chat_id, \
    get_need_for_rekick_players_id_by_chat_id
from controlers.player import get_game_by_person_msg_id
from controlers.user import get_user_by_user_id
from generation.generate import create_shelter, create_disaster, generate_person
from store import postgresDB
import asyncio
import datetime
from aiogram import types
from sqlalchemy.orm import Session

from controlers.game import get_game_by_chat_id, \
    get_players_usernames_by_chat_id, get_message_id_by_chat_id, get_players_id_by_chat_id, get_turn_by_chat_id
from controlers.player import get_player_by_user_id
from create_bot import bot
from generation.generate import generate_person, create_disaster
from models import Player
from store import postgresDB
from text.text_returner import get_me_text, get_bunker_text


async def start_game(callback: types.CallbackQuery):
    session = postgresDB.get_session()
    game = get_game_by_chat_id(str(callback.message.chat.id), session)
    if game is None or game.end_time:
        shelter = create_shelter()
        create_game(chat_id=str(callback.message.chat.id), start_message_id=callback.message.message_id,
                    size=shelter["size"], time_spent=shelter["time_spent"], disaster=create_disaster(),
                    condition=shelter["condition"], build_reason=shelter["build_reason"], location=shelter["location"],
                    room_1=shelter["room_1"], room_2=shelter["room_2"], room_3=shelter["room_3"],
                    available_resource_1=shelter["available_resource_1"],
                    available_resource_2=shelter["available_resource_2"],
                    session=session)
        # если в игре есть хотя бы один польователь
        buttons = [
            types.InlineKeyboardButton(text="Присоединиться",
                                       url=f"https://t.me/SllizBot?start={callback.message.chat.id}")
        ]
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(*buttons)
        await callback.message.answer(text="Нажмите кнопку, чтобы участвовать.", reply_markup=keyboard)
    await callback.answer()
    session.commit()
    session.close()


async def open_callback_handler(callback: types.CallbackQuery):
    session = postgresDB.get_session()
    open_param = callback.data.split('_')[1]
    open_text = ""
    user_id = callback.message.chat.id
    player = get_player_by_user_id(str(user_id), session)
    try:
        await bot.delete_message(chat_id=user_id, message_id=player.msg_id)
    except aiogram.utils.exceptions.MessageIdentifierNotSpecified:
        # игрок нажал на старое сообщение
        await callback.answer()
        session.close()
        return
    if open_param == "luggage":
        player.is_luggage_open = True
        open_text = f"Игрок <b>{player.username}</b> вскрыл свой <b>багаж: {player.luggage}</b>"
    elif open_param == "age":
        player.is_age_open = True
        player.is_sex_open = True
        open_text = f"Игрок <b>{player.username}</b> вскрыл свой <b>возраст и пол: {player.age}, {player.sex}</b>"
    elif open_param == "personality":
        player.is_personality_open = True
        open_text = f"Игрок <b>{player.username}</b> вскрыл свой <b>характер: {player.personality}</b>"
    elif open_param == "hobby":
        player.is_hobby_open = True
        open_text = f"Игрок <b>{player.username}</b> вскрыл свое <b>хобби: {player.hobby}</b>"
    elif open_param == "health":
        player.is_health_open = True
        open_text = f"Игрок <b>{player.username}</b> вскрыл свое <b>здоровье: {player.health}</b>"
    elif open_param == "fear":
        player.is_fear_open = True
        open_text = f"Игрок <b>{player.username}</b> вскрыл свою <b>фоббию: {player.fear}</b>"
    elif open_param == "add":
        player.is_add_inf_open = True
        open_text = f"Игрок <b>{player.username}</b> вскрыл свою <b>дополнительную информацию: {player.add_inf}</b>"
    elif open_param == "knowledge":
        player.is_knowledge_open = True
        open_text = f"Игрок <b>{player.username}</b> вскрыл свое <b>знание: {player.knowledge}</b>"
    chat_id = player.game.chat_id
    if get_turn_by_chat_id(str(chat_id), session) == 1:
        open_text = f"Игрок <b>{player.username}</b> вскрыл <b>профессию: {player.job}</b>\n" + open_text
    await bot.send_message(chat_id=chat_id,
                           text=open_text, parse_mode="HTML")
    player.is_open_param = True
    session.add(player)
    session.commit()
    session.close()

    session = postgresDB.get_session()
    alive_players = get_alive_players_id_by_chat_id(chat_id, session)
    cnt = 0
    for id in alive_players:
        player = get_player_by_user_id(id, session)
        cnt += player.is_open_param
    if cnt == len(alive_players):
        session.close()
        await discussion(chat_id)
    await callback.answer()
    session.close()


async def kick_callback_handler(callback: types.CallbackQuery):
    session = postgresDB.get_session()
    player = get_player_by_user_id(str(callback.from_user.id), session)
    if player.game and player.game.start_time < datetime.datetime.now() and player.game.end_time is None:
        player.is_vote = True
        session.add(player)
        session.commit()
        try:
            await bot.delete_message(chat_id=player.user_id, message_id=player.msg_id)
        except aiogram.utils.exceptions.MessageIdentifierNotSpecified:
            # нажал на старое сообщение
            session.close()
            await callback.answer()
            return
        player.msg_id = None
        open_param = callback.data.split('_')[1]
        player = get_player_by_user_id(open_param, session)
        player.voices_to_kick += 1

        session.add(player)
        session.commit()

        chat_id = get_player_by_user_id(str(callback.message.chat.id), session).game.chat_id
        cnt = 0
        alive_players = get_alive_players_id_by_chat_id(str(chat_id), session)

        for id in alive_players:
            player = get_player_by_user_id(id, session)
            cnt += player.is_vote
        if cnt == len(alive_players):
            session.close()
            await kick(chat_id)
    await callback.answer()
    session.close()


async def discussion(chat_id: str, array=None):
    session = postgresDB.get_session()
    res = await bot.send_message(chat_id=chat_id, text="<b>Время обсуждений!</b>", parse_mode="HTML")
    game = get_game_by_chat_id(chat_id, session)
    game.invite_link_to_chat = res.url
    session.add(game)
    session.commit()
    #await asyncio.sleep()
    for player in game.players:
        person_msg_game_ = get_game_by_person_msg_id(str(player.person_msg_id), session)
        if person_msg_game_ and person_msg_game_.end_time is None:  # проверка что чел в игре
            buttons = [types.InlineKeyboardButton(text="Бункер", callback_data="change_person_msg_to_shelter"),
                       types.InlineKeyboardButton(text="Апокалипсис", callback_data="change_person_msg_to_apocalypse"),
                       types.InlineKeyboardButton(text="Перейти в чат", url=f'{player.game.invite_link_to_chat}')]
            keyboard = types.InlineKeyboardMarkup(row_width=2)
            keyboard.add(*buttons)
            await bot.edit_message_text(message_id=player.person_msg_id,
                text=get_me_text(player),
                chat_id=player.user_id, reply_markup=keyboard, parse_mode="HTML")
    session.close()
    await vote(chat_id, array)


async def vote(chat_id: str, re_vote_people=None):
    session = postgresDB.get_session()
    button = types.InlineKeyboardButton(text="Голосовать", url="https://t.me/SllizBot")
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(button)
    res = await bot.send_message(chat_id=chat_id, text="<b>Время голосования!</b>", parse_mode="HTML", reply_markup=keyboard)
    game = get_game_by_chat_id(chat_id, session)
    game.invite_link_to_chat = res.url
    session.add(game)
    session.commit()
    for player in game.players:
        person_msg_game_ = get_game_by_person_msg_id(str(player.person_msg_id), session)
        if person_msg_game_ and person_msg_game_.end_time is None:  # проверка что чел в игре
            buttons = [types.InlineKeyboardButton(text="Бункер", callback_data="change_person_msg_to_shelter"),
                       types.InlineKeyboardButton(text="Апокалипсис", callback_data="change_person_msg_to_apocalypse"),
                       types.InlineKeyboardButton(text="Перейти в чат", url=f'{player.game.invite_link_to_chat}')]
            keyboard = types.InlineKeyboardMarkup(row_width=2)
            keyboard.add(*buttons)
            await bot.edit_message_text(message_id=player.person_msg_id,
                text=get_me_text(player),
                chat_id=player.user_id, reply_markup=keyboard, parse_mode="HTML")

    if re_vote_people is None:
        kickable = get_alive_players_id_by_chat_id(chat_id, session)
    else:
        kickable = get_need_for_rekick_players_id_by_chat_id(chat_id, session)
    alive_players = get_alive_players_id_by_chat_id(chat_id, session)
    for id in alive_players:
        buttons = create_buttons_to_voting(kickable, id, session)
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        keyboard.add(*buttons)
        player = get_player_by_user_id(id, session)
        res = await bot.send_message(chat_id=id, text="Выберите игрока, которого хотите кикнуть", reply_markup=keyboard)
        player.msg_id = res.message_id
        session.add(player)
        session.commit()

    #await asyncio.sleep(10)  # константное время настариваться
    #await bot.send_message(chat_id=chat_id, text="Время голосования кончилось!")

    session.close()


def create_buttons_to_voting(alive_players: list, current_player_user_id: str, session: Session):
    buttons = []
    for id in alive_players:
        player = get_player_by_user_id(id, session)
        if player.user_id != current_player_user_id:
            buttons.append(types.InlineKeyboardButton(text=f"{player.username}",
                                                      callback_data=f"kick_{player.user_id}"))
    return buttons


async def like_or_dislike_handler(callback: types.CallbackQuery):
    session = postgresDB.get_session()
    name, chat_id, kickable_player_id = callback.data.split('!')
    alive_players = get_alive_players_id_by_chat_id(chat_id, session)
    kickable_player = get_player_by_user_id(kickable_player_id, session)
    game = kickable_player.game
    player = get_player_by_user_id(str(callback.from_user.id), session)
    if not player.is_like_btn_pressed and player.user_id != kickable_player.user_id:
        if 'like' in name.split('_')[1]:
            if 'dislike' in name.split('_')[1]:
                game.dislikes += 1
            else:
                game.likes += 1
            session.add(game)
            session.commit()
            buttons = [types.InlineKeyboardButton(text=f"{game.likes} 👍", callback_data=f'press_like!{chat_id}!{kickable_player.user_id}'),
                       types.InlineKeyboardButton(text=f"{game.dislikes} 👎", callback_data=f'press_dislike!{chat_id}!{kickable_player.user_id}')]
            keyboard = types.InlineKeyboardMarkup(row_width=2)
            keyboard.add(*buttons)
            res = await bot.edit_message_text(chat_id=game.chat_id, message_id=game.final_vote_msg_id,
                                        text=f"Уцелевшие решили выгнать <b>{kickable_player.username}</b> из убежища."
                                                           f" <b>Вы действительно этого хотите?</b>",
                                     reply_markup=keyboard, parse_mode="HTML")

            game.invite_link_to_chat = res.url
            session.add(game)
            session.commit()
            for player in game.players:
                person_msg_game_ = get_game_by_person_msg_id(str(player.person_msg_id), session)
                if person_msg_game_ and person_msg_game_.end_time is None:  # проверка что чел в игре
                    buttons = [types.InlineKeyboardButton(text="Бункер", callback_data="change_person_msg_to_shelter"),
                               types.InlineKeyboardButton(text="Апокалипсис",
                                                          callback_data="change_person_msg_to_apocalypse"),
                               types.InlineKeyboardButton(text="Перейти в чат",
                                                          url=f'{game.invite_link_to_chat}')]
                    keyboard = types.InlineKeyboardMarkup(row_width=2)
                    keyboard.add(*buttons)
                    await bot.edit_message_text(message_id=player.person_msg_id,
                                                text=get_me_text(player),
                                                chat_id=player.user_id, reply_markup=keyboard, parse_mode="HTML")

            player.is_like_btn_pressed = True
            session.add(player)
            session.commit()
        if game.likes + game.dislikes + 1 == len(alive_players):
            if game.likes >= game.dislikes:
                await bot.send_message(chat_id=chat_id, text=f"Путем голосования выгнали: {kickable_player.username}")
                kickable_player.is_dead = True
                session.add(player)
                session.commit()
                if len(alive_players) - 1 > get_chat_by_telegram_id(str(chat_id), session).settings.max_players:
                    session.close()
                    await round(str(chat_id))
                else:
                    game.end_time = datetime.datetime.now()
                    await bot.send_message(chat_id=chat_id, text=f"Поздравляю игра закончилась")
                    session.add(game)
            else:
                game.likes = 0
                game.dislikes = 0
                session.add(game)
                await bot.send_message(chat_id=chat_id, text=f"Никого не кикнули")
                await round(str(chat_id))
    else:
        await callback.answer()
    session.commit()
    session.close()


async def kick(chat_id: str):
    session = postgresDB.get_session()
    alive_players = get_alive_players_id_by_chat_id(chat_id, session)
    max_voices_to_kick = -1
    kick_users_id = []
    for id in alive_players:
        player = get_player_by_user_id(id, session)
        if player.voices_to_kick > max_voices_to_kick:
            kick_users_id = [player.user_id]
            max_voices_to_kick = player.voices_to_kick
        elif player.voices_to_kick == max_voices_to_kick:
            kick_users_id.append(player.user_id)

    if len(kick_users_id) > 1:
        for id in kick_users_id:
            player = get_player_by_user_id(id, session)
            player.is_need_to_be_in_rekick_vote = True
            session.add(player)
            session.commit()
        session.close()
        await re_kick(chat_id, kick_users_id)
    else:
        game = get_game_by_chat_id(chat_id, session)
        player = get_player_by_user_id(kick_users_id[0], session)
        username = player.username
        buttons = [types.InlineKeyboardButton(text="👍", callback_data=f'press_like!{chat_id}!{player.user_id}'),
                   types.InlineKeyboardButton(text="👎", callback_data=f'press_dislike!{chat_id}!{player.user_id}')]
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        keyboard.add(*buttons)
        res = await bot.send_message(chat_id=chat_id, text=f"Уцелевшии решили выгнать <b>{username}</b> из убежища."
                                                           f" <b>Вы действительно этого хотите?</b>",
                                     reply_markup=keyboard, parse_mode="HTML")
        game.final_vote_msg_id = res.message_id
        session.add(game)
        session.commit()

    for id in alive_players:
        player = get_player_by_user_id(id, session)
        player.voices_to_kick = 0
        player.is_need_to_be_in_rekick_vote = False
        player.is_vote = False
        session.add(player)
        session.commit()
    session.close()


async def re_kick(chat_id: str, id_players: list):
    n = '\n•'
    session = postgresDB.get_session()
    await bot.send_message(chat_id=chat_id,
                           text=f"Игроки:\n•<b>{f'{n}'.join([get_player_by_user_id(id, session).username for id in id_players])}</b>"
                                f"\nНабрли <b>максимальное количество голосов.</b>"
                                f" Требуется <b>обсуждение и переголосвание.</b>",
                           parse_mode="HTML")
    session.close()
    await discussion(chat_id, id_players)


async def re_kick_vote(chat_id: str):
    session = postgresDB.get_session()
    await bot.send_message(chat_id=chat_id, text="<b>Время голосования!</b>", parse_mode="HTML")
    alive_players = get_alive_players_id_by_chat_id(chat_id, session)
    for id in alive_players:
        buttons = create_buttons_to_voting(alive_players, id, session)
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        keyboard.add(*buttons)
        player = get_player_by_user_id(id, session)
        res = await bot.send_message(chat_id=id, text="Выберите игрока, которого хотите <b>кикнуть</b>",
                                     reply_markup=keyboard, parse_mode="HTML")
        player.msg_id = res.message_id
        session.add(player)
        session.commit()
    session.close()
    await asyncio.sleep(10)  # константное время настариваться
    await bot.send_message(chat_id=chat_id, text="<b>Время голосования кончилось!</b>", parse_mode="HTML")


async def round(chat_id: str):
    session = postgresDB.get_session()
    game = get_game_by_chat_id(chat_id, session)
    game.turn += 1
    button = types.InlineKeyboardButton(text="Вскрыть", url="https://t.me/SllizBot")
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(button)
    if game.turn == 1:
        text_1 = "Каждому игроку необходимо вскрыть любой оставшийся параметр, <b>профессия вскроется автоматически</b>"
        text_2 = "Нажмите кнопку с нужной характеристикой, которая <b>вскроится вместе с вашей профессией</b>"
    else:
        text_1 = "Каждому игроку необходимо вскрыть <b>любой оставшийся параметр</b>"
        text_2 = "Нажмите кнопку с <b>нужной характеристикой</b>"
    res = await bot.send_message(chat_id=chat_id, text=text_1, reply_markup=keyboard, parse_mode="HTML")

    game.invite_link_to_chat = res.url
    session.add(game)
    session.commit()
    for player in game.players:
        person_msg_game_ = get_game_by_person_msg_id(str(player.person_msg_id), session)
        if person_msg_game_ and person_msg_game_.end_time is None:  # проверка что чел в игре
            buttons = [types.InlineKeyboardButton(text="Бункер", callback_data="change_person_msg_to_shelter"),
                       types.InlineKeyboardButton(text="Апокалипсис",
                                                  callback_data="change_person_msg_to_apocalypse"),
                       types.InlineKeyboardButton(text="Перейти в чат",
                                                  url=f'{game.invite_link_to_chat}')]
            keyboard = types.InlineKeyboardMarkup(row_width=2)
            keyboard.add(*buttons)
            await bot.edit_message_text(message_id=player.person_msg_id,
                                        text=get_me_text(player),
                                        chat_id=player.user_id, reply_markup=keyboard, parse_mode="HTML")

    for id in get_alive_players_id_by_chat_id(chat_id, session):
        buttons = await create_buttons_to_open_param(id, session)
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        keyboard.add(*buttons)
        res = await bot.send_message(chat_id=id,
                         text=text_2,
                         reply_markup=keyboard, parse_mode="HTML")
        player = get_player_by_user_id(id, session)
        player.msg_id = res.message_id
        session.add(player)
        session.commit()
    session.add(game)
    session.commit()
    session.close()


async def create_buttons_to_open_param(user_id: str, session: Session):
    player = get_player_by_user_id(user_id, session)
    buttons = []
    if not player.is_age_open and not player.is_sex_open:
        buttons.append(types.InlineKeyboardButton(text="Возраст и пол", callback_data="open_age_sex"))
    if not player.is_add_inf_open:
        buttons.append(types.InlineKeyboardButton(text="Доп. информация", callback_data="open_add_info"))
    if not player.is_personality_open:
        buttons.append(types.InlineKeyboardButton(text="Черта характера", callback_data="open_personality"))
    if not player.is_hobby_open:
        buttons.append(types.InlineKeyboardButton(text="Хобби", callback_data="open_hobby"))
    if not player.is_health_open:
        buttons.append(types.InlineKeyboardButton(text="Здоровье", callback_data="open_health"))
    if not player.is_luggage_open:
        buttons.append(types.InlineKeyboardButton(text="Багаж", callback_data="open_luggage"))
    if not player.is_fear_open:
        buttons.append(types.InlineKeyboardButton(text="Фоббия", callback_data="open_fear"))
    if not player.is_knowledge_open:
        buttons.append(types.InlineKeyboardButton(text="Знание", callback_data="open_knowledge"))
    #if not player.is_card_1_open:
    #    buttons.append(types.InlineKeyboardButton(text="Использовать карточку 1", callback_data="use1"))
    #if not player.is_card_2_open:
    #    buttons.append(types.InlineKeyboardButton(text="Использовать карточку 2", callback_data="use2"))
    return buttons


async def change_person_msg_to_apocalypse(callback: types.CallbackQuery):
    session = postgresDB.get_session()
    user_id = callback.from_user.id
    player = get_player_by_user_id(str(user_id), session)
    if player is None:
        await callback.answer()
        session.close()
        return
    person_msg_game_ = get_game_by_person_msg_id(str(player.person_msg_id), session)
    if person_msg_game_ and person_msg_game_.end_time is None:

        buttons = [types.InlineKeyboardButton(text="Бункер", callback_data="change_person_msg_to_shelter"),
                   types.InlineKeyboardButton(text="Характеристики", callback_data="change_person_msg_to_me"),
                   types.InlineKeyboardButton(text="Перейти в чат", url=f'{player.game.invite_link_to_chat}')]
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        keyboard.add(*buttons)
        try:
            await bot.edit_message_text(message_id=player.person_msg_id, text=f"<b>{player.game.disaster}</b>",
                                    chat_id=callback.from_user.id, reply_markup=keyboard, parse_mode="HTML")
        except aiogram.utils.exceptions.MessageToEditNotFound:
            await callback.answer()  # человек нажал на старое сообщение
    else:
        await callback.answer()
    session.close()


async def change_person_msg_to_shelter(callback: types.CallbackQuery):
    # здесь
    session = postgresDB.get_session()
    user_id = callback.from_user.id
    player = get_player_by_user_id(str(user_id), session)
    if player is None:
        await callback.answer()
        session.close()
        return
    person_msg_game_ = get_game_by_person_msg_id(str(player.person_msg_id), session)
    if person_msg_game_ and person_msg_game_.end_time is None:
        buttons = [types.InlineKeyboardButton(text="Характеристики", callback_data="change_person_msg_to_me"),
                   types.InlineKeyboardButton(text="Апокалипсис", callback_data="change_person_msg_to_apocalypse"),
                   types.InlineKeyboardButton(text="Перейти в чат", url=f'{player.game.invite_link_to_chat}')]
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        keyboard.add(*buttons)
        try:
            await bot.edit_message_text(message_id=player.person_msg_id,
                                text=get_bunker_text(player.game), chat_id=callback.from_user.id,
                                reply_markup=keyboard, parse_mode="HTML")
        except aiogram.utils.exceptions.MessageToEditNotFound:
            await callback.answer()  # человек нажал на старое сообщение
    else:
        await callback.answer()
    session.close()


async def change_person_msg_to_me(callback: types.CallbackQuery):
    # здесь
    session = postgresDB.get_session()
    user_id = callback.from_user.id
    player = get_player_by_user_id(str(user_id), session)
    if player is None:
        await callback.answer()
        session.close()
        return
    person_msg_game_ = get_game_by_person_msg_id(str(player.person_msg_id), session)
    if person_msg_game_ and person_msg_game_.end_time is None:  # проверка что чел в игре
        buttons = [types.InlineKeyboardButton(text="Бункер", callback_data="change_person_msg_to_shelter"),
                   types.InlineKeyboardButton(text="Апокалипсис", callback_data="change_person_msg_to_apocalypse"),
                   types.InlineKeyboardButton(text="Перейти в чат", url=f'{player.game.invite_link_to_chat}')]
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        keyboard.add(*buttons)
        try:
            await bot.edit_message_text(message_id=player.person_msg_id,
                                text=get_me_text(player),
                                chat_id=callback.from_user.id, reply_markup=keyboard, parse_mode="HTML")
        except aiogram.utils.exceptions.MessageToEditNotFound:
            await callback.answer() # человек нажал на старое сообщение
    else:
        await callback.answer()
    session.close()


async def activate_card_handler(callback: types.CallbackQuery):
    _, card_type = callback.data.split('!')
    session = postgresDB.get_session()
    user_id = callback.from_user.id
    player = get_player_by_user_id(str(user_id), session)
    #player.is_card_1_open = True  !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    session.add(player)
    await close_card_panel_handler(callback)
    await card_action_handler(card_type, user_id)
    #await bot.answer_callback_query(callback.id, text="Карточка действий активирована", show_alert=True)
    session.commit()
    session.close()


async def close_card_panel_handler(callback: types.CallbackQuery):
    session = postgresDB.get_session()
    user_id = callback.from_user.id
    player = get_player_by_user_id(str(user_id), session)
    await bot.delete_message(chat_id=user_id, message_id=player.card_msg_id)
    player.card_msg_id = None
    session.add(player)
    session.commit()
    session.close()


async def card_action_handler(card_type: str, user_id: str, to_user_id=None, second=False):
    session = postgresDB.get_session()
    if "exchange_card" in card_type:
        '''карта обмена'''
        cur_player = get_player_by_user_id(str(user_id), session)
        game = cur_player.game
        buttons = []
        for i in get_alive_players_id_by_chat_id(game.chat_id, session):
            player = get_player_by_user_id(i, session)
            if player != cur_player:
                buttons.append(types.InlineKeyboardButton(text=player.username,
                                                          callback_data=f"card_selected_player_{card_type}!{player.user_id}"))
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        keyboard.add(*buttons)
        tmp = {"health": "здоровьем", "job": "профессией", "personality": "характером", "hobby": "хобби",
               "luggage": "багажом", "inf": "доп. информацией", "fear": "фобией", "knowledge": "знанием"}
        param = tmp[card_type.split('_')[-1]]
        res = await bot.send_message(chat_id=user_id,
                                     text=f"Выберете игрока, с которым хотите обменяться <b>{param}</b>",
                                     parse_mode="HTML", reply_markup=keyboard)
        cur_player.card_msg_id = res.message_id
        session.add(cur_player)
    elif "open_card" in card_type:
        '''открыть чужую характеристику'''
        cur_player = get_player_by_user_id(str(user_id), session)
        game = cur_player.game
        buttons = []

        for i in get_alive_players_id_by_chat_id(game.chat_id, session):
            player = get_player_by_user_id(i, session)
            if player != cur_player:
                if "open_card_health" in card_type:
                    if not player.is_health_open:
                        if second:
                            buttons.append(types.InlineKeyboardButton(text=player.username,
                                                                      callback_data=f"{card_type}!{player.user_id}"))
                        else:
                            buttons.append(types.InlineKeyboardButton(text=player.username,
                                                                      callback_data=f"card_selected_player_{card_type}!{player.user_id}"))
                elif "open_card_fear" in card_type:
                    if not player.is_fear_open:
                        buttons.append(types.InlineKeyboardButton(text=player.username,
                                                                  callback_data=f"card_selected_player_{card_type}!{player.user_id}"))
                elif "open_card_hobby" in card_type:
                    if not player.is_hobby_open:
                        buttons.append(types.InlineKeyboardButton(text=player.username,
                                                                  callback_data=f"card_selected_player_{card_type}!{player.user_id}"))
                elif "open_card_personality" in card_type:
                    if not player.is_personality_open:
                        if second:
                            buttons.append(types.InlineKeyboardButton(text=player.username,
                                                                      callback_data=f"{card_type}!{player.user_id}"))
                        else:
                            buttons.append(types.InlineKeyboardButton(text=player.username,
                                                                      callback_data=f"card_selected_player_{card_type}!{player.user_id}"))
                elif "open_card_add_inf" in card_type:
                    if not player.is_add_inf_open:
                        buttons.append(types.InlineKeyboardButton(text=player.username,
                                                                  callback_data=f"card_selected_player_{card_type}!{player.user_id}"))
                elif "open_card_knowledge" in card_type:
                    if not player.is_knowledge_open:
                        buttons.append(types.InlineKeyboardButton(text=player.username,
                                                                  callback_data=f"card_selected_player_{card_type}!{player.user_id}"))
                elif "open_card_luggage" in card_type:
                    if not player.is_luggage_open:
                        buttons.append(types.InlineKeyboardButton(text=player.username,
                                                                  callback_data=f"card_selected_player_{card_type}!{player.user_id}"))
        if len(buttons) == 0:
            tmp = {"health": "здоровье", "job": "профессия", "personality": "характер", "hobby": "хобби",
                   "luggage": "багаж", "inf": "доп. информация", "fear": "фобия", "knowledge": "знание"}
            param = card_type.split('!')[0].split('_')[-1]
            button = types.InlineKeyboardButton(text="Закрыть",
                                                callback_data=f"close_card_message!{cur_player.user_id}")
            keyboard = types.InlineKeyboardMarkup(row_width=2)
            keyboard.add(button)
            res = await bot.send_message(chat_id=cur_player.user_id,
                                         text=f"Упс.. У всех игроков <b>уже вскрыт</b> этот параметр: <b>{tmp[param]}</b>",
                                         parse_mode="HTML",
                                         reply_markup=keyboard)
            cur_player.card_msg_id = res.message_id

        else:
            keyboard = types.InlineKeyboardMarkup(row_width=2)
            keyboard.add(*buttons)
            tmp = {"health": "здоровье", "personality": "характер", "hobby": "хобби",
                   "luggage": "багаж", "inf": "доп. информацию", "fear": "фобию", "knowledge": "знание"}
            param = tmp[card_type.split('_')[-1]]
            if second:
                text_ = f"Игрок {get_player_by_user_id(to_user_id, session).username} только что вскрыл <b>{param}</b>." \
                        f" Вам необходимо ёще раз выбрать игрока, которому необходимо вскрыть <b>{param}</b>"
            else:
                text_ = f"Выберете игрока, которому необходимо вскрыть <b>{param}</b>"
            res = await bot.send_message(chat_id=cur_player.user_id,
                                         text=text_,
                                         parse_mode="HTML",
                                         reply_markup=keyboard)
            cur_player.card_msg_id = res.message_id
        session.add(cur_player)
    session.commit()
    session.close()


async def card_selected_player_handler(callback: types.CallbackQuery):
    session = postgresDB.get_session()
    card_type, to_user_id = map(str, callback.data.split('!'))
    if "exchange_card" in card_type:
        '''карта обмена'''
        cur_player = get_player_by_user_id(str(callback.from_user.id), session)
        to_player = get_player_by_user_id(to_user_id, session)
        if "personality" in card_type:
            tmp_param = cur_player.personality
            cur_player.personality = to_player.personality
            to_player.personality = tmp_param
            tmp_param = cur_player.is_personality_open
            cur_player.is_personality_open = to_player.is_personality_open
            to_player.is_personality_open = tmp_param
        elif "job" in card_type:
            tmp_param = cur_player.job
            cur_player.job = to_player.job
            to_player.job = tmp_param
            tmp_param = cur_player.is_job_open
            cur_player.is_job_open = to_player.is_job_open
            to_player.is_job_open = tmp_param
        elif "health" in card_type:
            tmp_param = cur_player.health
            cur_player.health = to_player.health
            to_player.health = tmp_param
            tmp_param = cur_player.is_health_open
            cur_player.is_health_open = to_player.is_health_open
            to_player.is_health_open = tmp_param
        elif "hobby" in card_type:
            tmp_param = cur_player.hobby
            cur_player.hobby = to_player.hobby
            to_player.hobby = tmp_param
            tmp_param = cur_player.is_hobby_open
            cur_player.is_hobby_open = to_player.is_hobby_open
            to_player.is_hobby_open = tmp_param
        elif "fear" in card_type:
            tmp_param = cur_player.fear
            cur_player.fear = to_player.fear
            to_player.fear = tmp_param
            tmp_param = cur_player.is_fear_open
            cur_player.is_fear_open = to_player.is_fear_open
            to_player.is_fear_open = tmp_param
        elif "luggage" in card_type:
            tmp_param = cur_player.luggage
            cur_player.luggage = to_player.luggage
            to_player.luggage = tmp_param
            tmp_param = cur_player.is_luggage_open
            cur_player.is_luggage_open = to_player.is_luggage_open
            to_player.is_luggage_open = tmp_param
        elif "add_inf" in card_type:
            tmp_param = cur_player.add_inf
            cur_player.add_inf = to_player.add_inf
            to_player.add_inf = tmp_param
            tmp_param = cur_player.is_add_inf_open
            cur_player.is_add_inf_open = to_player.is_add_inf_open
            to_player.is_add_inf_open = tmp_param
        elif "knowledge" in card_type:
            tmp_param = cur_player.knowledge
            cur_player.knowledge = to_player.knowledge
            to_player.knowledge = tmp_param
            tmp_param = cur_player.is_knowledge_open
            cur_player.is_knowledge_open = to_player.is_knowledge_open
            to_player.is_knowledge_open = tmp_param

        session.add(cur_player)
        session.add(to_player)
        session.commit()

        if cur_player.game.turn == 1:
            text_ = "Нажмите кнопку с нужной характеристикой, которая <b>вскроится вместе с вашей профессией</b>"
        else:
            text_ = "Нажмите кнопку с <b>нужной характеристикой</b>"

        buttons = await create_buttons_to_open_param(cur_player.user_id, session)
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        keyboard.add(*buttons)
        try:
            await bot.edit_message_text(message_id=cur_player.msg_id,
                                    text=text_,
                                    chat_id=cur_player.user_id,
                                    reply_markup=keyboard, parse_mode="HTML")
        except (MessageNotModified, MessageToEditNotFound):
            pass

        buttons = await create_buttons_to_open_param(to_player.user_id, session)
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        keyboard.add(*buttons)
        try:
            await bot.edit_message_text(message_id=to_player.msg_id,
                                    text=text_,
                                    chat_id=to_player.user_id,
                                    reply_markup=keyboard, parse_mode="HTML")
        except (MessageNotModified, MessageToEditNotFound):
            pass
        buttons = [types.InlineKeyboardButton(text="Характеристики", callback_data="change_person_msg_to_me"),
                   types.InlineKeyboardButton(text="Апокалипсис", callback_data="change_person_msg_to_apocalypse")]
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        keyboard.add(*buttons)

        await bot.edit_message_text(message_id=cur_player.person_msg_id,
                                    text=get_me_text(cur_player),
                                    chat_id=cur_player.user_id,
                                    reply_markup=keyboard, parse_mode="HTML")
        await bot.edit_message_text(message_id=to_player.person_msg_id,
                                    text=get_me_text(to_player),
                                    chat_id=to_player.user_id,
                                    reply_markup=keyboard, parse_mode="HTML")
        await bot.send_message(chat_id=cur_player.game.chat_id,
                               text=f"Игрок <b>{cur_player.username}</b> использовал "
                                    f"карточку действий: <b>{cur_player.card_1.split('!')[1]}</b> "
                                    f"на игрока <b>{to_player.username}</b>", parse_mode="HTML")
        await bot.delete_message(chat_id=callback.from_user.id, message_id=cur_player.card_msg_id)
        #cur_player.msg_id
    elif "open_card" in card_type:
        cur_player = get_player_by_user_id(str(callback.from_user.id), session)
        to_player = get_player_by_user_id(to_user_id, session)
        if "personality" in card_type:
            if to_player.is_personality_open:
                await bot.delete_message(message_id=cur_player.card_msg_id, chat_id=cur_player.user_id)
                session.commit()
                cur_player_user_id: str = cur_player.user_id
                to_player_user_id: str = to_player.user_id
                session.commit()
                session.close()
                await card_action_handler(card_type, cur_player_user_id, to_player_user_id, True)
                return
            else:
                to_player.is_personality_open = True
                await bot.send_message(chat_id=to_player.game.chat_id,
                                       text=f"Игрок <b>{cur_player.username}</b> вскрыл <b>характера {to_player.username}</b> с помощью карточки действий."
                                            f"\nХарактер игрока: <b>{to_player.personality}</b>", parse_mode="HTML")
                await bot.delete_message(chat_id=cur_player.user_id, message_id=cur_player.card_msg_id)
                session.add(to_player)
                session.commit()
                if cur_player.game.turn == 1:
                    text_ = "Нажмите кнопку с нужной характеристикой, которая <b>вскроится вместе с вашей профессией</b>"
                else:
                    text_ = "Нажмите кнопку с <b>нужной характеристикой</b>"

                buttons = await create_buttons_to_open_param(to_player.user_id, session)
                keyboard = types.InlineKeyboardMarkup(row_width=2)
                keyboard.add(*buttons)
                try:
                    await bot.edit_message_text(message_id=to_player.msg_id,
                                                text=text_,
                                                chat_id=to_player.user_id,
                                                reply_markup=keyboard, parse_mode="HTML")
                except (MessageNotModified, MessageToEditNotFound):
                    pass

        elif "health" in card_type:
            if to_player.is_health_open:
                await bot.delete_message(message_id=cur_player.card_msg_id, chat_id=cur_player.user_id)
                session.commit()
                cur_player_user_id: str = cur_player.user_id
                to_player_user_id: str = to_player.user_id
                session.commit()
                session.close()
                await card_action_handler(card_type, cur_player_user_id, to_player_user_id, True)
                return
            else:
                to_player.is_health_open = True
                await bot.send_message(chat_id=to_player.game.chat_id,
                                       text=f"Игрок <b>{cur_player.username}</b> вскрыл <b>здоровье {to_player.username}</b> с помощью карточки действий."
                                            f"\nЗдоровье игрока: <b>{to_player.health}</b>", parse_mode="HTML")
                await bot.delete_message(chat_id=cur_player.user_id, message_id=cur_player.card_msg_id)
                session.add(to_player)
                session.commit()
                if cur_player.game.turn == 1:
                    text_ = "Нажмите кнопку с нужной характеристикой, которая <b>вскроится вместе с вашей профессией</b>"
                else:
                    text_ = "Нажмите кнопку с <b>нужной характеристикой</b>"

                buttons = await create_buttons_to_open_param(to_player.user_id, session)
                keyboard = types.InlineKeyboardMarkup(row_width=2)
                keyboard.add(*buttons)
                try:
                    await bot.edit_message_text(message_id=to_player.msg_id,
                                                text=text_,
                                                chat_id=to_player.user_id,
                                                reply_markup=keyboard, parse_mode="HTML")
                except (MessageNotModified, MessageToEditNotFound):
                    pass
        elif "hobby" in card_type:
            if to_player.is_hobby_open:
                await bot.delete_message(message_id=cur_player.card_msg_id, chat_id=cur_player.user_id)
                session.commit()
                cur_player_user_id: str = cur_player.user_id
                to_player_user_id: str = to_player.user_id
                session.commit()
                session.close()
                await card_action_handler(card_type, cur_player_user_id, to_player_user_id, True)
                return
            else:
                to_player.is_hobby_open = True
                await bot.send_message(chat_id=to_player.game.chat_id,
                                       text=f"Игрок <b>{cur_player.username}</b> вскрыл <b>хобби {to_player.username}</b> с помощью карточки действий."
                                            f"\nХобби игрока: <b>{to_player.hobby}</b>", parse_mode="HTML")
                await bot.delete_message(chat_id=cur_player.user_id, message_id=cur_player.card_msg_id)
                session.add(to_player)
                session.commit()
                if cur_player.game.turn == 1:
                    text_ = "Нажмите кнопку с нужной характеристикой, которая <b>вскроится вместе с вашей профессией</b>"
                else:
                    text_ = "Нажмите кнопку с <b>нужной характеристикой</b>"

                buttons = await create_buttons_to_open_param(to_player.user_id, session)
                keyboard = types.InlineKeyboardMarkup(row_width=2)
                keyboard.add(*buttons)
                try:
                    await bot.edit_message_text(message_id=to_player.msg_id,
                                                text=text_,
                                                chat_id=to_player.user_id,
                                                reply_markup=keyboard, parse_mode="HTML")
                except (MessageNotModified, MessageToEditNotFound):
                    pass
        elif "fear" in card_type:
            if to_player.is_fear_open:
                await bot.delete_message(message_id=cur_player.card_msg_id, chat_id=cur_player.user_id)
                session.commit()
                cur_player_user_id: str = cur_player.user_id
                to_player_user_id: str = to_player.user_id
                session.commit()
                session.close()
                await card_action_handler(card_type, cur_player_user_id, to_player_user_id, True)
                return
            else:
                to_player.is_fear_open = True
                await bot.send_message(chat_id=to_player.game.chat_id,
                                       text=f"Игрок <b>{cur_player.username}</b> вскрыл <b>фобию {to_player.username}</b> с помощью карточки действий."
                                            f"\nФобию игрока: <b>{to_player.fear}</b>", parse_mode="HTML")
                await bot.delete_message(chat_id=cur_player.user_id, message_id=cur_player.card_msg_id)
                session.add(to_player)
                session.commit()
                if cur_player.game.turn == 1:
                    text_ = "Нажмите кнопку с нужной характеристикой, которая <b>вскроится вместе с вашей профессией</b>"
                else:
                    text_ = "Нажмите кнопку с <b>нужной характеристикой</b>"

                buttons = await create_buttons_to_open_param(to_player.user_id, session)
                keyboard = types.InlineKeyboardMarkup(row_width=2)
                keyboard.add(*buttons)
                try:
                    await bot.edit_message_text(message_id=to_player.msg_id,
                                                text=text_,
                                                chat_id=to_player.user_id,
                                                reply_markup=keyboard, parse_mode="HTML")
                except (MessageNotModified, MessageToEditNotFound):
                    pass
        elif "luggage" in card_type:
            if to_player.is_luggage_open:
                await bot.delete_message(message_id=cur_player.card_msg_id, chat_id=cur_player.user_id)
                session.commit()
                cur_player_user_id: str = cur_player.user_id
                to_player_user_id: str = to_player.user_id
                session.commit()
                session.close()
                await card_action_handler(card_type, cur_player_user_id, to_player_user_id, True)
                return
            else:
                to_player.is_luggage_open = True
                await bot.send_message(chat_id=to_player.game.chat_id,
                                       text=f"Игрок <b>{cur_player.username}</b> вскрыл <b>багаж {to_player.username}</b> с помощью карточки действий."
                                            f"\nБагаж игрока: <b>{to_player.luggage}</b>", parse_mode="HTML")
                await bot.delete_message(chat_id=cur_player.user_id, message_id=cur_player.card_msg_id)
                session.add(to_player)
                session.commit()
                if cur_player.game.turn == 1:
                    text_ = "Нажмите кнопку с нужной характеристикой, которая <b>вскроится вместе с вашей профессией</b>"
                else:
                    text_ = "Нажмите кнопку с <b>нужной характеристикой</b>"

                buttons = await create_buttons_to_open_param(to_player.user_id, session)
                keyboard = types.InlineKeyboardMarkup(row_width=2)
                keyboard.add(*buttons)
                try:
                    await bot.edit_message_text(message_id=to_player.msg_id,
                                                text=text_,
                                                chat_id=to_player.user_id,
                                                reply_markup=keyboard, parse_mode="HTML")
                except (MessageNotModified, MessageToEditNotFound):
                    pass
        elif "add_inf" in card_type:
            if to_player.is_add_inf_open:
                await bot.delete_message(message_id=cur_player.card_msg_id, chat_id=cur_player.user_id)
                session.commit()
                cur_player_user_id: str = cur_player.user_id
                to_player_user_id: str = to_player.user_id
                session.commit()
                session.close()
                await card_action_handler(card_type, cur_player_user_id, to_player_user_id, True)
                return
            else:
                to_player.is_add_inf_open = True
                await bot.send_message(chat_id=to_player.game.chat_id,
                                       text=f"Игрок <b>{cur_player.username}</b> "
                                            f"вскрыл <b>доп. информацию {to_player.username}</b> с помощью карточки действий."
                                            f"\nДоп. информация игрока: <b>{to_player.add_inf}</b>", parse_mode="HTML")
                await bot.delete_message(chat_id=cur_player.user_id, message_id=cur_player.card_msg_id)
                session.add(to_player)
                session.commit()
                if cur_player.game.turn == 1:
                    text_ = "Нажмите кнопку с нужной характеристикой, которая <b>вскроится вместе с вашей профессией</b>"
                else:
                    text_ = "Нажмите кнопку с <b>нужной характеристикой</b>"

                buttons = await create_buttons_to_open_param(to_player.user_id, session)
                keyboard = types.InlineKeyboardMarkup(row_width=2)
                keyboard.add(*buttons)
                try:
                    await bot.edit_message_text(message_id=to_player.msg_id,
                                                text=text_,
                                                chat_id=to_player.user_id,
                                                reply_markup=keyboard, parse_mode="HTML")
                except (MessageNotModified, MessageToEditNotFound):
                    pass
        elif "knowledge" in card_type:
            if to_player.is_knowledge_open:
                await bot.delete_message(message_id=cur_player.card_msg_id, chat_id=cur_player.user_id)
                session.commit()
                cur_player_user_id: str = cur_player.user_id
                to_player_user_id: str = to_player.user_id
                session.commit()
                session.close()
                await card_action_handler(card_type, cur_player_user_id, to_player_user_id, True)
                return
            else:
                to_player.is_knowledge_open = True
                await bot.send_message(chat_id=to_player.game.chat_id,
                                       text=f"Игрок <b>{cur_player.username}</b> "
                                            f"вскрыл <b>знание {to_player.username}</b> с помощью карточки действий."
                                            f"\nЗнание игрока: <b>{to_player.knowledge}</b>",
                                       parse_mode="HTML")
                await bot.delete_message(chat_id=cur_player.user_id, message_id=cur_player.card_msg_id)
                session.add(to_player)
                session.commit()
                if cur_player.game.turn == 1:
                    text_ = "Нажмите кнопку с нужной характеристикой, которая <b>вскроится вместе с вашей профессией</b>"
                else:
                    text_ = "Нажмите кнопку с <b>нужной характеристикой</b>"

                buttons = await create_buttons_to_open_param(to_player.user_id, session)
                keyboard = types.InlineKeyboardMarkup(row_width=2)
                keyboard.add(*buttons)
                try:
                    await bot.edit_message_text(message_id=to_player.msg_id,
                                                text=text_,
                                                chat_id=to_player.user_id,
                                                reply_markup=keyboard, parse_mode="HTML")
                except (MessageNotModified, MessageToEditNotFound):
                    pass
        # когда я нажимаю если у игрока вскрыто значит он только что вскрыл свое знание
        session.add(to_player)
        session.add(cur_player)
        session.commit()
    session.close()


async def close_card_message_handler(callback: types.CallbackQuery):
    _, cur_user_id = map(str, callback.data.split('!'))
    session = postgresDB.get_session()
    player = get_player_by_user_id(cur_user_id, session)
    await bot.delete_message(message_id=player.card_msg_id, chat_id=player.user_id)
    session.close()