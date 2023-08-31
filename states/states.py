from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from create_bot import bot
from create_bot import dp


class GameStates(StatesGroup):
    START = State()
    FIRST_OPEN = State()
    SECOND_OPEN = State()
    THIRD_OPEN = State()
    FORTH_OPEN = State()
    FIVE_OPEN = State()
    SIX_OPEN = State()
    SEVEN_OPEN = State()