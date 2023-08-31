from aiogram import types
from create_bot import bot
import os


async def web_app_(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(row_width=1)  # создаем клавиатуру
    webAppTest = types.WebAppInfo(url=os.getenv('WEBAPP_URL'))  # создаем webappinfo - формат хранения url
    butt = types.KeyboardButton(text="НАСТРОЙКИ", web_app=webAppTest)  # создаем кнопку типа webapp
    keyboard.add(butt)  # добавляем кнопки в клавиатуру
    keyboard.resize_keyboard = True
    await bot.send_message(chat_id=message.chat.id, text="<b>Нажмити на кнопку ниже, чтобы настроить игру</b>",
                           reply_markup=keyboard, parse_mode="HTML")


async def answer(webAppData: types.WebAppData):
    settings = webAppData.__dict__["_values"]["web_app_data"]["data"]
    print(settings)
    await bot.send_message(chat_id=str(webAppData.__dict__["_values"]["from"]["id"]),
                           text=f"<b>Настройки успешно сохранены\n{settings}</b>", reply_markup=types.ReplyKeyboardRemove(),
                           parse_mode="HTML")

