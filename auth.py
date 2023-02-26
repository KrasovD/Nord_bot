from aiogram import executor, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor

from bot import dp, bot
import api

# Регистрация
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
    customer  = api.Api(message)
    info = customer.client_info()
    if info.id:
        # новая сфм с функциями и запись id пользователя в свою БД
        message.answer(text='''
        {} у вас {} баллов
        '''.format(info.name, info.available)
                       )
    else:
        await message.answer(
            text='''
            Вы не зарегистрированы или ввели номер не верно.
            Попробуйте еще раз
            '''
        )
        await Login.again


@dp.message_handler(state=Login.again)
async def process_name(message: types.Message, state: FSMContext):
    if 1:
        await message.answer('Успешно')
    else:
        key1 = types.InlineKeyboardButton(text='Служба поддержки', callback_data='help')
        key2 = types.InlineKeyboardButton(text='Регистрация', callback_data='registration')
        keyboard = types.InlineKeyboardMarkup().add(key1, key2)
        await Login.finish
        await message.answer(
            text='''
            Не могу найти, возможно Вас нет в программе лояльности
            ''',
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
    

'''@dp.message_handler(lambda message: message.text.isdigit(), state=Form.count)
async def process_age(message: types.Message, state: FSMContext):
    Добавление кол-ва ингридиента
    # Обновление шага и значения count
    await Form.next()
    await state.update_data(count=int(message.text))

    # Добавление Inline клавиатуры
    key1 = types.InlineKeyboardButton(text='Добавить', callback_data='next')
    key2 = types.InlineKeyboardButton(text='Закончить', callback_data='fin')
    keyboard = types.InlineKeyboardMarkup().add(key1, key2)

    await message.answer("Добавить еще ингридиент?", reply_markup=keyboard)

@dp.callback_query_handler(lambda call: call.data, state=Form.finish)
async def call_info(call: types.CallbackQuery, state: FSMContext):

    # Если продолжаем, возвращается к первому шагу
    if call.data == 'next':  
        await bot.answer_callback_query(call.id)
        await Form.first()
        await bot.send_message(call.from_user.id, text='Ингридиент:', reply_markup=types.ReplyKeyboardRemove())
        async with state.proxy() as data:
            data_ingr.append((data['ingredient'],data['count']))
    # Если заканчиваем, то выходим из FSM и выводим данные
    if call.data == 'fin':
        await bot.answer_callback_query(call.id)
        async with state.proxy() as data:
            data_ingr.append((data['ingredient'],data['count']))
            text = ''
            for num, d in enumerate(data_ingr):
                text += '{}.{}: {} (гр)\n'.format(num+1, d[0], d[1])
            await bot.send_message(
                call.from_user.id,
                text=text,
                reply_markup=types.ReplyKeyboardRemove()
            )
        await Form.next()
        await bot.send_message(call.from_user.id, 'Введите цену:')
        


@dp.callback_query_handler(lambda call: call.data, state=Form.price)
async def call_info(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'Yes':
        await bot.answer_callback_query(call.id)
        dish.add_dish()
        for data in data_ingr:
            dish.add_ingredient(data[0], data[1])
        await state.finish()
    if call.data == 'No':
        await bot.answer_callback_query(call.id)
        await state.finish()

@dp.message_handler(lambda message: message.text, state=Form.price)
async def process_price(message: types.Message, state: FSMContext):
    dish.price = int(message.text)
    key1 = types.InlineKeyboardButton(text='Да', callback_data='Yes')
    key2 = types.InlineKeyboardButton(text='Нет', callback_data='No')
    keyboard = types.InlineKeyboardMarkup().add(key1, key2)
    await message.answer('Сохранить?', reply_markup=keyboard)


@dp.message_handler(lambda message: message.text, state=Form.finish)
async def process_gender_invalid(message: types.Message):
    """
    Валидация клавиш (Добавить, Закончить)
    """
    return await message.reply("Выбирите, пожалуйста")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)'''