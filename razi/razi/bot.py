import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from razi.config.config import BOT_TOKEN
from razi.handlers.handlers import start_bot, name_food, get_food
from razi.states.states import ListFood

import pika


def main():
    logging.basicConfig(level=logging.INFO)

    bot = Bot(token=BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(bot, storage=storage)

    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='hello')

    dp.register_message_handler(start_bot, commands=["start"])
    dp.register_message_handler(name_food, commands=["recipe"])
    dp.register_message_handler(get_food, state=ListFood.list_food)

    executor.start_polling(dp, skip_updates=True)


if __name__ == "__main__":
    main()
