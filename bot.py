import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.utils import executor
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage

import config
import api
from model import *

logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


@dp.message_handler(commands=['start'])
async def show_hello(message: types.Message):
    '''Сообщение при старте бота'''

    # поиск в локальной БД гостя по telegram_id
    customer = find_customer(message.chat.id)

    if customer.telegram_id:
        await message.answer(text='С возвращением {}'.format(customer.name))
        # создание объекта гость с данными из QuickResto
        guest = api.Api(customer.number)
        info = guest.client_info()  # базовая информация о госте
        await message.answer(text='{} у вас {} баллов'.format(info.name, info.available))
    else:
        key1 = types.InlineKeyboardButton(
            text='Вход', callback_data='login')
        key2 = types.InlineKeyboardButton(
            text='Регистрация', callback_data='registration')
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
            ''', reply_markup=keyboard
        )


@dp.message_handler(commands=['history'])
async def show_history(message: types.Message):
    '''Вывод истории транзакций пользователя'''

    # поиск в локальной БД гостя по telegram_id
    customer = find_customer(message.chat.id)
    if customer.telegram_id:
        # создание объекта гость с данными из QuickResto
        guest = api.Api(customer.number)
        await message.answer(text='{}'.format(guest.client_history()))
    else:
        await message.answer(text='Вы не вошли. Введите команду /start')


@dp.message_handler(commands=['balance'])
async def show_balance(message: types.Message):
    '''Вывод актуального баланса пользователя'''

    # поиск в локальной БД гостя по telegram_id
    customer = find_customer(message.chat.id)
    if customer.telegram_id:
        # создание объекта гость с данными из QuickResto
        guest = api.Api(customer.number)
        info = guest.client_info()  # базовая информация о госте
        await message.answer(text='{} у вас {} баллов'.format(info.name, info.available))
    else:
        await message.answer(text='Вы не вошли. Введите команду /start')


@dp.message_handler(commands=['qr'])
async def show_qr(message: types.Message):
    '''Вывод QR кода пользователя для его индетификации в программе лояльности'''

    # создание объекта гость с данными из QuickResto
    customer = find_customer(message.chat.id)
    if customer.telegram_id:
        # базовая информация о госте
        guest = api.Api(customer.number)
        await message.answer_photo(photo=guest.qr_code())
    else:
        await message.answer(text='Вы не вошли. Введите команду /start')


@dp.callback_query_handler(lambda call: call.data)
async def call_info(call: types.CallbackQuery):
    '''Захват нажатие кнопки после старта бота, регистрация или вход'''

    if call.data == 'login':
        await Login.check.set()  # Вход в SFM входа
        await bot.send_message(
            chat_id=call.from_user.id,
            text='''
            Ваш номер: (Пример: 79874352121)
            '''
        )

    if call.data == 'registration':
        await Registration.check()  # Вход в SFM регистрации


class Registration(StatesGroup):
    check = State()
    number = State()
    finish = State()


class Login(StatesGroup):
    registration = State()  # Регистрация номого пользователя
    check = State()  # Проверка номера в БД
    again = State()
    finish = State()


@dp.message_handler(state=Login.check)
async def process_name(message: types.Message, state: FSMContext):
    """
    Проверка в БД QuickResto номера или индетификационного номера
    """
    customer = api.Api(
        message.text)  # создание объекта гость с данными из QuickResto
    info = customer.client_info()  # базовая информация о госте
    if info.id:
        await message.answer(text='{} у вас {} баллов'.format(info.name, info.available))
        try:
            # добавление гостя в локальную БД
            add_customer(message.chat.id,
                         message.from_user.full_name, message.text)
        except:
            pass
        await state.finish()  # выход из SFM, т.к гость найдет в QuickResto
    else:
        await Login.again.set()  # переход к повоторному вопросу
        await message.answer(
            text='Вы не зарегистрированы или ввели номер не верно. Попробуйте еще раз'
        )


@dp.message_handler(state=Login.again)
async def process_name(message: types.Message, state: FSMContext):
    ''''
    Повторная проверка номера и помощь или регистрация в случае отсутствия
    '''

    # создание объекта гость с данными из QuickResto
    customer = api.Api(message.text)
    info = customer.client_info()  # базовая информация о госте
    if info.id:
        await message.answer(text='{} у вас {} баллов'.format(info.name, info.available))
        try:
            # добавление гостя в локальную БД
            add_customer(message.chat.id,
                         message.from_user.full_name, message.text)
        except:
            pass
        await state.finish()  # выход из SFM, т.к гость найдет в QuickResto
    else:
        key1 = types.InlineKeyboardButton(
            text='Служба поддержки', callback_data='help')
        key2 = types.InlineKeyboardButton(
            text='Регистрация', callback_data='registration')
        keyboard = types.InlineKeyboardMarkup().add(key1, key2)
        # переход к перехвату нажатия кнопок
        await Login.finish.set()
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
    if call.data == 'registration':  # переход в SFM регистрации
        await Registration.number.set()


@dp.message_handler(state=Registration.check)
async def check_number(message: types.Message, state: FSMContext):
    '''
    Проверка номера при регистрации на наличие в БД QiuckResto
    '''
    customer = api.Api(
        message.text)  # создание объекта гость с данными из QuickResto
    info = customer.client_info()  # базовая информация о госте
    if info.id:
        await message.answer(text='Вы уже зарегистрированы!')
        await message.answer(text='{} у вас {} баллов'.format(info.name, info.available))
        await state.finish()  # выход из SFM
    else:
        await message.answer(text='''
Ваш номер: (Пример: 79874352121). 
Если вы не хотите вводить свой номер, можете ввести любой уникальный набор цифр')'''
                             )
        await state.next()  # переход к шагу ввода номера


@dp.message_handler(state=Registration.number)
async def check_number(message: types.Message, state: FSMContext):
    '''
    Проверка номера на число
    '''
    if (message.text).isdigit():
        async with state.proxy() as data:
            data['number'] = message.text
        await message.answer(text='''
Спасибо, что Вы с нами! 
'''.format(message.from_user.first_name, message.from_user.last_name))
        await state.next()  # переход к шагу проверки данных
    else:
        await message.answer(text='Вводите только цифры!')


@dp.message_handler(state=Registration.finish)
async def check_number(message: types.Message, state: FSMContext):
    '''
    Проверка данных, добавление пользователя в локальную БД,
    и вывод базовой информации и пользоватиле
    '''
    async with state.proxy() as data:
        add_customer(message.chat.id,
                     message.from_user.full_name, data['number'])
        await message.answer(text='''
Вы зарегистрированы
Ваш номер {}
Ваше имя {}'''.format(data['number'], data['name']))

    await state.finish()  # выход из SFM


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
