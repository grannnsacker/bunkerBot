from aiogram.utils import executor


from create_bot import dp
from handlers import register
from store import postgresDB


register.register_handlers_client(dp)
executor.start_polling(dp, skip_updates=True)
