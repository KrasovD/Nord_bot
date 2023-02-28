'''
Создание моделей и обьектов локальной БД,
и функции работы с ней
'''

from peewee import *

conn = SqliteDatabase('customer.db')

class BaseModel(Model):
    '''Базовая модель с привязкой к файлу БД'''
    class Meta:
        database = conn

class Customer(BaseModel):
    '''Модель пользователя'''

    telegram_id = IntegerField(column_name='Telegram_id', primary_key=True)
    name = TextField(column_name='Name')
    number = IntegerField(column_name='Number')
    birthday = DateField(column_name='Birthday', null=True)

# Соединение с БД и попытка создать таблицу, если не создана
conn.connect()
try:
    conn.create_tables([Customer])
except:
    pass

def add_customer(telegram_id, name, number, birthday=None) -> Customer:
    '''Cоздания пользователя'''
    customer =  Customer.create(
            telegram_id=telegram_id,
            name=name,
            number=number,
            birthday=birthday)
    return customer

def find_customer(telegram_id) -> Customer:
    '''Поиск пользователя по telegram_id'''
    return Customer.get(Customer.telegram_id==telegram_id)