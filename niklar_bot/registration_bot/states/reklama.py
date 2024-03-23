from aiogram.fsm.state import State, StatesGroup

class Adverts(StatesGroup):
    adverts = State()
    first_name = State()
    last_name = State()
    phone_number = State()
    address = State()
    email = State()
    photo = State()
    country = State()
    city = State()
    planet = State()
    house_number = State()