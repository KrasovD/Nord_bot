import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.utils import executor
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage

import config
import api

logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

number = None

@dp.message_handler(commands=['start'])
async def show_hello(message: types.Message):
    '''Сообщение при старте бота'''

    key1 = types.InlineKeyboardButton(text='Вход', callback_data='login')
    key2 = types.InlineKeyboardButton(text='Регистрация', callback_data='registration')
    keyboard = types.InlineKeyboardMarkup().add(key1, key2)
    await message.answer(
            text='''
Здраствуйте, {}!
Добро пожаловать в систему лояльности Kos.Place.
Мы начисляем 5% с каждого чека на ваш бонусный счет,
и в дальнейшем можем списать до 50% из суммы чека из
ваших бонусов.'''.format(message.chat.first_name)
            )
    await message.answer(
        text='''
Если вы уже зарегестрированы у нас в бонусной программе,
нажмите вход и введите номер, который указывали при регистрации.
Если вы впервые у нас, то нажмите регистрация
и введите ваш номер или любой другой индетификационный номер
        ''',
        reply_markup=keyboard
        )


@dp.callback_query_handler(lambda call: call.data)
async def call_info(call: types.CallbackQuery):
    if call.data == 'login':
        await Login.check.set()
        await bot.send_message(
            chat_id=call.from_user.id, 
            text='''
            Ваш номер: (Пример: 79874352121)
            '''
        )
        
    if call.data == 'registration':
        pass
    if call.data == 'help':
        pass

class Registration(StatesGroup):
    number = State()
    name = State()
    birthday = State()
    finish = State()

# Авторизация
class Login(StatesGroup):
    registration = State() # Регистрация номого пользователя
    check = State()  # Проверка номера в БД
    again = State()
    finish = State()



@dp.message_handler(state=Login.check)
async def process_name(message: types.Message, state: FSMContext):
    """
    Проверка в БД QuickResto номера или индетификационного номера
    """
    customer  = api.Api(message.text)
    info = customer.client_info()
    if info.id:
        # новая сфм с функциями и запись id пользователя в свою БД
        await message.answer(text='{} у вас {} баллов'.format(info.name, info.available))
        await state.finish()
    else:
        await Login.again.set()
        await message.answer(
            text='Вы не зарегистрированы или ввели номер не верно. Попробуйте еще раз'
        )


@dp.message_handler(state=Login.again)
async def process_name(message: types.Message, state: FSMContext):
    customer  = api.Api(message.text)
    info = customer.client_info()
    if info.id:
        await message.answer(text='{} у вас {} баллов'.format(info.name, info.available))
        await state.finish()
    else:
        key1 = types.InlineKeyboardButton(text='Служба поддержки', callback_data='help')
        key2 = types.InlineKeyboardButton(text='Регистрация', callback_data='registration')
        keyboard = types.InlineKeyboardMarkup().add(key1, key2)
        await state.finish()
        await message.answer(
            text='Не могу найти, возможно Вас нет в программе лояльности',
            reply_markup=keyboard
        )

dp.callback_query_handler(lambda call: call.data, state=Login.finish)
async def call_info(call: types.CallbackQuery, state: FSMContext):
    '''
    Перехват нажатия кнопки
    '''
    
    if call.data == 'help':  # отправка в службу поддержки
        await bot.send_message(call.from_user.id, 'Служба поддержки в разработке')
    if call.data == 'registration':
        await Registration.number
    

'''@dp.message_handler(content_types='text')
async def command(message:types.Message):
    if (message.text).isdigit():
        if api.Customer(message.text):
            key1 = types.KeyboardButton(text='bonuses')
            key2 = types.KeyboardButton(text='history')
            key3 = types.KeyboardButton(text='qr_code')
            reply = types.ReplyKeyboardMarkup().add(key1, key2, key3)
            await message.answer('Вы являетесь участником бонусной программы, у вас {} баллов'.format(client.client_bonuses()), reply_markup=reply)
        else:
            key1 = types.InlineKeyboardButton(text='Да', callback_data='yes_reg')
            key2 = types.InlineKeyboardButton(text='Нет', callback_data='no_reg')
            markup = types.InlineKeyboardMarkup().add(key1, key2)
            await message.answer('Вы не участник бонусной программы. Хотите зарегистрироваться?', reply_markup=markup)
    if message.text == 'bonuses':
        await message.answer('{}, у Вас {} бонусов'.format(message.chat.first_name, client.client_bonuses()))
    if message.text == 'history':
        await message.answer('{}'.format(client.client_history()))
    if message.text == 'qr_code':
        await message.answer_photo(client.qr_code())'''


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)