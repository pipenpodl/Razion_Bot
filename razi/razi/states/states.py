from aiogram.dispatcher.filters.state import State, StatesGroup


class ListFood(StatesGroup):
    list_food = State()
