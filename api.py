import requests
import config
import json
import qrcode
from pprint import pprint
import datetime


class Customer():
    '''Базовая информация об клиентах'''

    def __init__(self, id = None, accounts = None, type = None, date = None, tokens = None, firstName = '', lastName = '', **kwargs):
        self.id = id
        if (accounts != None): self.available = accounts[0]['accountBalance']['available']
        self.name = firstName + lastName
        self.type = type
        self.tokens: list = tokens
        self.date = date


class Api():
    '''Выгрузка данных из CRM об клиента и бонусах'''

    headers = {
        'Connection': 'keep-alive',
        'Content-Type': 'application/json',
    }
    URL = 'https://{login}.quickresto.ru/platform/online/'.format(login=config.login)

    def __init__(self, number): 
        self.number = number # Номер телефона клиента


    def datetime_format(self, date):
        timedelta = datetime.timedelta(hours=3)
        return (datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M:%S.%fZ') + timedelta).strftime('%d.%m %H:%M')

    def json_format(self, data):
        return str(data).replace('\'', '"').replace(' ', '').encode('utf-8')
    
    def post(self, url, data):
        return requests.post(url=url, auth=(config.login, config.password), headers=self.headers, data=data).json()

    def client_info(self):
        '''Выгрузка базовой информации о клиенте  (поиск по номеру телефона)'''

        url = self.URL + 'bonuses/customerInfo'
        data = {
            "customerToken":{
                "type": "phone",
                "entry": "manual",
                "key": self.number
            }
        }
        return Customer(**self.post(url, self.json_format(data)))

    def format_history(self, regTime, type, amount):
        '''Шаблон истории начисления\списания баллов'''

        if type == 'DEBIT_CONFIRMATION':
            type = 'Списание'
        elif type == 'CREDIT': 
            type = 'Начисление'
        else: return False

        return 'Дата: {}. {}: {} баллов'.format(self.datetime_format(regTime), type, amount )

    def client_history(self):
        '''История транзакций в бонусной системе клиента'''

        url = self.URL + 'bonuses/operationHistory'
        data = {
            "customerToken": {
                "type": "phone",
                "entry": "manual",
                "key": number
            }, 
            "accountType": {
                "accountGuid": "bonus_account_type-1"
            }
        }
        return [self.format_history(data['regTime'], data['type'], data['amount'])  for data in self.post(url, self.json_format(data))['transactions']]

    def save_json(self, response):
        '''Сохранение данных из API в json формате'''

        with open('data.json', 'w') as base:
            json.dump(response, base)

    def qr_code(self):
        '''Формирование QR кода'''

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(self.number)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        print(img.save('%s.png' % self.number))
        return open('%s.png' %self.number, 'rb')
    

class CustomerOperation(Api):
    '''Операции с клиентсикими обьектами'''

    def createObject(self, firstName='', lastName='', number=''):
        url = self.URL + 'bonuses/createCustomer'
        data = {
            'firstName': firstName,
            'lastName': lastName,
            #'dateOfBirth': datetime, #'1990-03-07T19:00:00.000Z'
            'tokens': [{
                'type': 'phone',
                'entry': 'manual',
                'key': number
                },{
                'type': 'card',
                'entry': 'barCode',
                'key': number
                }  
            ],
        }

        return self.post(url, self.json_format(data))

    def updateObject(self):
        params = {
            "moduleName": 'crm.customer',
            "ownerContextId": 'ownerContextId',
            "ownerContextClassName": 'ownerContextClassName',
            "parentContextId": 'parentContextId',
            "parentContextClassName": 'parentContextClassName'
        }

        json_data = object.get_json_object()

        return self.post(self.URL+'api/update', parameters=params, json_data=json_data)

         


if __name__ == '__main__':
    number = '736389'
    create = CustomerOperation(number)
    pprint(create.createObject('тест', 'тест', number))