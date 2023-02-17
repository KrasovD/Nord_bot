import requests
import config
import json
import qrcode
from pprint import pprint


class Api():
    '''Выгрузка данных из CRM об клиента и бонусах'''
    headers = {
        'Connection': 'keep-alive',
        'Content-Type': 'application/json',
    }
    url = 'https://{login}.quickresto.ru/platform/online/'.format(login=config.login)

    def __init__(self, number):
        self.number = number # Номер телефона клиента

    def post(self, url, data):
        return requests.post(url=url, auth=(config.login, config.password), headers=self.headers, data=data).json()

    def client_info(self):
        '''Выгрузка базовой информации о клиенте'''
        url = self.url + 'bonuses/customerInfo'
        data = '{"customerToken":{"type":"phone","entry":"manual","key":"%s"}}' %self.number
        json_data = self.post(url, data)
        return Customer(**json_data)
        #print(response['accounts'][0]['accountBalance']['available'])

    def format_history(self, regTime, type, amount):
        if type == 'DEBIT_CONFIRMATION':
            type = 'Списание'
        elif type == 'CREDIT': 
            type = 'Начисление'
        else: return False

        return 'Дата: {}\n{}: {} баллов'.format(regTime, type, amount )

    def client_history(self):
        '''История транзакций в бонусной системе клиента'''
        url = self.url + 'bonuses/operationHistory'
        data = '{"customerToken":{"type":"phone","entry":"manual","key":"%s"}, "accountType":{"accountGuid":"bonus_account_type-1"}}' % self.number
        return [self.format_history(data['regTime'], data['type'], data['amount'])  for data in self.post(url, data)['transactions']]

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


class Customer(Api):
    def __init__(self, id = None, accounts = None, type = None, date = None, token = None, firstName = None, lastName = None, **kwargs):
        self.id = id
        if (accounts != None): self.available = accounts[0]['accountBalance']['available']
        self.name = firstName + lastName
        self.type = type
        self.tokens: list = token
        self.date = date
         


if __name__ == '__main__':
    api = Api('79969290700')
    pprint(api.client_history())