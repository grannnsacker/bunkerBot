from aiogram import Bot
from aiogram.dispatcher import Dispatcher
import os
from dotenv import load_dotenv, find_dotenv
from aiogram.contrib.fsm_storage.memory import MemoryStorage



load_dotenv(find_dotenv())

bot = Bot(token=os.getenv('TOKEN'))

dp = Dispatcher(bot)