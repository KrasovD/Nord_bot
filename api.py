import requests
import json
import qrcode
import datetime

import config


class Customer():
    '''Базовая информация об клиентах'''

    def __init__(self, id = None, 
                 accounts = None, 
                 type = None, 
                 date = None, 
                 tokens = None, 
                 firstName = '', 
                 lastName = '', 
                 **kwargs):
        self.id = id # id
        if (accounts != None): self.available = accounts[0]['accountBalance']['available'] # баланс 
        self.name = firstName + lastName # имя, фамилия
        self.type = type # тип аккаунта
        self.tokens: list = tokens # индетификационые ключи
        self.date = date # дата регистрации

class Api():
    '''
    Выгрузка данных из CRM об клиента (история транцакций,
    баланс бонусов, формирование QR кода для авторизации)
    
    '''

    headers = {
        'Connection': 'keep-alive',
        'Content-Type': 'application/json',
    }
    # url для входа в API QuickResto
    URL = 'https://{login}.quickresto.ru/platform/online/'.format(login=config.login) 

    def __init__(self, number): 
        self.number = number # Номер телефона клиента


    def _datetime_format(self, date) -> str:
        '''Преобразование даты и времени из QickResto'''
        timedelta = datetime.timedelta(hours=3)
        return (datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M:%S.%fZ') + timedelta).strftime('%d.%m %H:%M')

    def _json_format(self, data) -> str:
        '''Преобразование словаря в читаемый API QR формат'''
        return str(data).replace('\'', '"').replace(' ', '').encode('utf-8')
    
    def _post(self, url, data) -> requests:
        '''Post запрос в API QuickResto и возврат в json формате'''
        return requests.post(url=url, auth=(config.login, config.password), headers=self.headers, data=data).json()
    
    def _save_json(self, response) -> None:
        '''Сохранение данных из API в json формате'''
        with open('data.json', 'w') as base:
            json.dump(response, base)

    def _format_history(self, history) -> str:
        '''Шаблон текста истории начисления\списания баллов'''
        text = list()
        for data in history:
            if data['type'] == 'DEBIT_CONFIRMATION':
                data['type'] = 'Списание'
            elif data['type'] == 'CREDIT': 
                data['type'] = 'Начисление'
            else:
                break
            text.append('{}: {} ({})\n'.format(data['type'], data['amount'], self._datetime_format(data['regTime'])))
        return ''.join(reversed(text))
    
    def client_info(self) -> Customer:
        '''Выгрузка базовой информации о клиенте  (поиск по номеру телефона)'''

        url = self.URL + 'bonuses/customerInfo'
        data = {
            "customerToken":{
                "type": "phone",
                "entry": "manual",
                "key": self.number
            }
        }
        return Customer(**self._post(url, self._json_format(data)))

    def client_history(self):
        '''История транзакций в бонусной системе клиента'''

        url = self.URL + 'bonuses/operationHistory'
        data = {
            "customerToken": {
                "type": "phone",
                "entry": "manual",
                "key": self.number
            }, 
            "accountType": {
                "accountGuid": "bonus_account_type-1"
            }
        }
        return self._format_history(self._post(url, self._json_format(data))['transactions'])

    def qr_code(self):
        '''Формирование QR кода'''
        try:
            return open('files/qr/qr_%d.png'%self.number, 'rb')
        except:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(self.number)
            img = qr.make_image(fill_color="black", back_color="white")
            img.save('files/qr/qr_%d.png'%self.number)
            return open('files/qr/qr_%d.png'%self.number, 'rb')
        
      

class CustomerOperation(Api):
    '''Операции с клиентсикими обьектами'''

    def createObject(self, firstName='', lastName='', number=''):
        ''' Создание гостя в системе QuickResto'''

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

        return self._post(url, self._json_format(data))

# в разработке ........

    def updateObject(self):
        ''' Изменение данных о госте в QuickResto'''
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
    pass