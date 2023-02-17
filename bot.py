import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.utils import executor

import config
import api

logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.TOKEN)
dp = Dispatcher(bot)

number = None

@dp.message_handler(commands=['start'])
async def show_hello(message: types.Message):
    '''Сообщение при старте бота'''
    await message.answer(
            text='''
            Привет, {}!
            Введите ваш номер для идентификация в нашей системе лояльности (начиная с 7)
            '''.format(message.chat.first_name)
            )


@dp.message_handler(content_types='text')
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
        await message.answer_photo(client.qr_code())


@dp.callback_query_handler(lambda call: call.data)
async def call_info(call: types.CallbackQuery):
    if call.data == 'yes_reg':
        await bot.send_photo(chat_id=call.from_user.id, photo=client.qr_code())
        
    if call.data == 'no_reg':
        await bot.send_message(chat_id=call.from_user.id, text='Ну ладно =(')

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)