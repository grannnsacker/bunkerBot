from aiogram import types
from aiogram.dispatcher import Dispatcher
from handlers.callback_query_handlers import start_game, open_callback_handler, kick_callback_handler, \
    change_person_msg_to_apocalypse, change_person_msg_to_shelter, change_person_msg_to_me, activate_card_handler, \
    close_card_panel_handler, card_selected_player_handler, close_card_message_handler
from handlers.message_handlers import command_start, command_go, cancel_game, command_me, command_card, command_profile, \
    rights
from handlers.webApp import web_app_, answer


def register_handlers_client(dp: Dispatcher):
    dp.register_message_handler(answer, content_types=['web_app_data'])
    dp.register_message_handler(command_start, commands=['start', 'help'])
    dp.register_message_handler(command_go, commands=['go'])  # закончить рег и начать играть
    dp.register_message_handler(cancel_game, commands=['cancel'])  # закончить игру
    dp.register_message_handler(command_card, commands=['card'])  # отработка карточки действий
    dp.register_message_handler(command_me, commands=['me'])  # отработка вывода
    dp.register_message_handler(web_app_, commands=['web'])  # отработка вывода
    dp.register_message_handler(command_profile, commands=['profile'])  # отработка вывода
    dp.register_message_handler(rights, commands=['rights'])  # отработка вывода
    dp.register_callback_query_handler(start_game, lambda x: "start_game" in x.data)
    dp.register_callback_query_handler(close_card_message_handler, lambda x: "close_card_message" in x.data)
    # отработка закрытия панель карты, когда нечего вскрыт
    dp.register_callback_query_handler(open_callback_handler, lambda x: "open" in x.data and "card" not in x.data)
    dp.register_callback_query_handler(kick_callback_handler, lambda x: "kick" in x.data)
    dp.register_callback_query_handler(activate_card_handler, lambda x: "activate_action_card" in x.data)
    dp.register_callback_query_handler(card_selected_player_handler, lambda x: "card_selected_player" in x.data)
    dp.register_callback_query_handler(change_person_msg_to_apocalypse, text="change_person_msg_to_apocalypse")
    dp.register_callback_query_handler(close_card_panel_handler, text="close_card_panel")
    dp.register_callback_query_handler(change_person_msg_to_shelter, text="change_person_msg_to_shelter")
    dp.register_callback_query_handler(change_person_msg_to_me, text="change_person_msg_to_me")


