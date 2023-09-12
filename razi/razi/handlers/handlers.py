from aiogram import types
from aiogram.dispatcher import FSMContext
import asyncio

from razi.states.states import ListFood

import aio_pika


API_QUEUE_NAME = "api_queue"
BOT_QUEUE_NAME = "bot_queue"


loop = asyncio.get_event_loop()

# Инициализация соединения и канала RabbitMQ
async def init_rabbitmq():
    connection = await aio_pika.connect_robust("amqp://guest:guest@localhost/")
    channel = await connection.channel()
    return connection, channel

connection, channel = loop.run_until_complete(init_rabbitmq())


async def send_message_to_queue(text):
    # Эта функция отправляет сообщение в очередь api_queue
    await channel.default_exchange.publish(
        aio_pika.Message(body=text.encode()),
        routing_key=API_QUEUE_NAME,
    )


async def wait_for_response():
    while True:
        # Эта функция ожидает ответ из очереди bot_queue и возвращает его
        queue = await channel.declare_queue(BOT_QUEUE_NAME, auto_delete=False)

        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    return message.body.decode()

        await asyncio.sleep(1)            


async def start_bot(message: types.Message):
    await message.answer('''
        👨🏼‍🍳Дорогие гурманы! Я ваш шеф-повар, готовый вас порадовать великолепными блюдами. Добро пожаловать в мир кулинарных вдохновений!

👉🏼Чтобы начать, скажите мне, что у вас есть в холодильнике, и я приготовлю для вас невероятные рецепты, используя доступные ингредиенты. Просто отправьте команду /recipe, и мы начнем творить волшебство на вашей кухне!
    ''')


async def name_food(message: types.Message):
    await message.answer("Давай составим список продуктов которые у тебя есть. Введи продукты одним сообщением (разделяйте запятыми).")

    # Set state
    await ListFood.list_food.set()


async def validate_input(user_input):
    # Разбиваем введенный текст на отдельные слова по запятым
    words = user_input.split(',')
    # Проверяем каждое слово
    for word in words:  
        
        if word.isdigit():
            return False
        
    
    return True


async def get_food(message: types.Message, state: FSMContext):
    await state.update_data(l_food=message.text)

    data = await state.get_data()

    if await validate_input(data["l_food"]):
        await send_message_to_queue(data["l_food"])
        await message.answer("Ваши продукты отправлены, ожидайте рецепты")
        await message.answer(await wait_for_response())
                    
        # Входим в состояние ожидания возраста
        await state.finish()

    else:
        await message.reply("Неправильный формат, попробуйте снова /recipe (введите продукты через зяпятую)")
        await state.finish()

