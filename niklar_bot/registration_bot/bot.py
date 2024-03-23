from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart,Command
from aiogram import F
from aiogram.types import Message
from data import config
import asyncio
import logging
import sys
from menucommands.set_bot_commands  import set_default_commands
from baza.sqlite import Database
from filters.admin import IsBotAdminFilter
from filters.check_sub_channel import IsCheckSubChannels
from keyboard_buttons import admin_keyboard
from aiogram.fsm.context import FSMContext
from middlewares.throttling import ThrottlingMiddleware #new
from states.reklama import Adverts
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
import time 
import re 
ADMINS = config.ADMINS
TOKEN = config.BOT_TOKEN
CHANNELS = config.CHANNELS

dp = Dispatcher()


@dp.message(CommandStart())
async def start_command(message:Message,state:FSMContext):
    full_name = message.from_user.full_name
    telegram_id = message.from_user.id
    try:
        db.add_user(full_name=full_name,telegram_id=telegram_id)
        await message.answer(text="Assalomu alaykum, botimizga hush kelibsiz, ism kiriting")
        await state.set_state(Adverts.first_name)
    except:
        await message.answer(text="Assalomu alaykum")


@dp.message(IsCheckSubChannels())
async def kanalga_obuna(message:Message):
    text = ""
    inline_channel = InlineKeyboardBuilder()
    for index,channel in enumerate(CHANNELS):
        ChatInviteLink = await bot.create_chat_invite_link(channel)
        inline_channel.add(InlineKeyboardButton(text=f"{index+1}-kanal",url=ChatInviteLink.invite_link))
    inline_channel.adjust(1,repeat=True)
    button = inline_channel.as_markup()
    await message.answer(f"{text} kanallarga azo bo'ling",reply_markup=button)



#Admin panel uchun
@dp.message(Command("admin"),IsBotAdminFilter(ADMINS))
async def is_admin(message:Message):
    await message.answer(text="Admin menu",reply_markup=admin_keyboard.admin_button)


@dp.message(F.text=="Foydalanuvchilar soni",IsBotAdminFilter(ADMINS))
async def users_count(message:Message):
    counts = db.count_users()
    text = f"Botimizda {counts[0]} ta foydalanuvchi bor"
    await message.answer(text=text)

@dp.message(F.text=="Reklama yuborish",IsBotAdminFilter(ADMINS))
async def advert_dp(message:Message,state:FSMContext):
    await state.set_state(Adverts.adverts)
    await message.answer(text="Reklama yuborishingiz mumkin !")

@dp.message(Adverts.adverts)
async def send_advert(message:Message,state:FSMContext):
    
    message_id = message.message_id
    from_chat_id = message.from_user.id
    users = await db.all_users_id()
    count = 0
    for user in users:
        try:
            await bot.copy_message(chat_id=user[0],from_chat_id=from_chat_id,message_id=message_id)
            count += 1
        except:
            pass
        time.sleep(0.5)
    
    await message.answer(f"Reklama {count}ta foydalanuvchiga yuborildi")
    await state.clear()



#-----------------------------------------------------------------


@dp.message(Adverts.first_name)
async def get_first_name(message:Message,state:FSMContext):
    pattern = "^[a-z0-9_-]{3,15}$";
    if re.match(pattern,message.text): 
     first_name = message.text
     await state.update_data(first_name=first_name)

     await state.set_state(Adverts.last_name)
     text = f"Familyangizni kiriting!"
     await message.reply(text=text)
    
    else:
        await message.reply(text="Ismingizni noto'g'ri kiritdingiz")
@dp.message(Adverts.last_name)
async def get_last_name(message:Message,state:FSMContext):
    pattern = "^[a-z0-9_-]{3,15}$"
    if re.match(pattern,message.text): 
     last_name = message.text
     await state.update_data(last_name=last_name)

     await state.set_state(Adverts.email)
     text = f"Emailingizni kiriting!"
     await message.reply(text=text) 
    
    else:
        await message.reply(text="Familiyangizni noto'g'ri kiritdingiz")

@dp.message(Adverts.email)
async def get_email(message:Message,state:FSMContext):
    pattern = "[^@ \t\r\n]+@[^@ \t\r\n]+\.[^@ \t\r\n]+"
    if re.match(pattern,message.text):

        email = message.text
        await state.update_data(email=email)

        await state.set_state(Adverts.photo)
        text = f"Rasmingizni yuboring!"
        await message.reply(text=text)
    
    else:
        await message.reply(text="Emailingizni noto'g'ri kiritdingiz")

@dp.message(Adverts.photo,F.photo)
async def get_photo(message:Message,state:FSMContext):
    photo = message.photo[-1].file_id 
    await state.update_data(photo=photo)
    await state.set_state(Adverts.phone_number)
    text = f"Telefon nomeringizni kiriting!"
    await message.reply(text=text)

@dp.message(Adverts.photo)
async def not_get_photo(message:Message,state:FSMContext):
    text = f"Iltimos rasm yuboring!"
    await message.reply(text=text)




@dp.message(Adverts.phone_number)
async def get_phone_number(message:Message,state:FSMContext):
    pattern = "^[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}$"
    if re.match(pattern,message.text):

        phone_number = message.text
        await state.update_data(phone_number=phone_number)

        await state.set_state(Adverts.planet)
        text = f" Vazningizni kiriting!"
        await message.reply(text=text)
    
    else:
        await message.reply(text="telefon nomeringizni noto'g'ri kiritdingiz")



@dp.message(Adverts.planet)
async def get_planet(message:Message,state:FSMContext):
        planet = message.text
        await state.update_data(planet=planet)

        await state.set_state(Adverts.city)
        text = f"shaxringizni nomini kiriting!"
        await message.reply(text=text)

@dp.message(Adverts.planet)
async def not_get_planet(message:Message,state:FSMContext):
    text = f"Vazningizni kiriting!"
    await message.reply(text=text)        


@dp.message(Adverts.city)
async def get_city(message:Message,state:FSMContext):

        city = message.text
        await state.update_data(city=city)

        await state.set_state(Adverts.country)
        text = f"Mamalakatingizni kiriting!"
        await message.reply(text=text)


@dp.message(Adverts.city)
async def not_get_city(message:Message,state:FSMContext):
    text = f"Iltimos shahringizni nomini kiriting!"
    await message.reply(text=text)

@dp.message(Adverts.country)
async def get_country(message:Message,state:FSMContext):

        country = message.text
        await state.update_data(country=country)

        await state.set_state(Adverts.house_number)
        text = f"uyingiz raqamini kiriting kiriting!"
        await message.reply(text=text)

@dp.message(Adverts.country)
async def not_get_country(message:Message,state:FSMContext):
    text = f"Viloyatingizni kiriting!"
    await message.reply(text=text)      


@dp.message(Adverts.house_number)
async def get_house_number(message:Message,state:FSMContext):

        house_number = message.text
        await state.update_data(house_number=house_number)

        await state.set_state(Adverts.address)
        text = f"Mahallangizni kiriting!"
        await message.reply(text=text) 

@dp.message(Adverts.house_number)
async def not_get_house_number(message:Message,state:FSMContext):
    text = f"Yoqtirgan raqam kiriting!"
    await message.reply(text=text)           

      


@dp.message(Adverts.address)
async def get_address(message:Message,state:FSMContext):
    address = message.text
    await state.update_data(address=address)




    data = await state.get_data()    
    my_photo = data.get("photo") 
    first_name = data.get("first_name")
    last_name = data.get("last_name")
    phone_number = data.get("phone_number")
    address = data.get("address")
    email = data.get("email")
    photo = data.get("photo")
    country = data.get("country")
    city = data.get("city")
    planet = data.get("city")
    house_number = data.get("house_number")

    text = f"<b>Ariza</b>\nIsmi: {first_name}\nFamilyasi: {last_name}\nTel: {phone_number}\nManzil: {address}\nGmail: {email}\nMamalakat: {country}\nShahar: {city}\nSayyora: {planet}\nUy raqami: {house_number}"
    
    

    await bot.send_photo(ADMINS[0],photo=my_photo,caption=text)
    print(first_name,last_name,phone_number,address,)
    

    await state.clear()
    text = f"Siz muvaffaqiyatli tarzda ro'yhatdan o'tdingiz🎉"
    await message.reply(text=text)



@dp.startup()
async def on_startup_notify(bot: Bot):
    for admin in ADMINS:
        try:
            await bot.send_message(chat_id=int(admin),text="Bot ishga tushdi")
        except Exception as err:
            logging.exception(err)

#bot ishga tushganini xabarini yuborish
@dp.shutdown()
async def off_startup_notify(bot: Bot):
    for admin in ADMINS:
        try:
            await bot.send_message(chat_id=int(admin),text="Bot ishdan to'xtadi!")
        except Exception as err:
            logging.exception(err)




async def main() -> None:
    global bot,db
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
    db = Database(path_to_db="main.db")
    db.create_table_users()
    await set_default_commands(bot)
    dp.message.middleware(ThrottlingMiddleware(slow_mode_delay=0.5))
    await dp.start_polling(bot)
    




if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    asyncio.run(main())
