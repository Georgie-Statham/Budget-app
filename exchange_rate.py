import requests
import json
from decimal import *


def get_exchange_rate(date):
    """ gets the GBP/ILS exchange rate for a specified date """
    response = requests.get(
        'https://api.exchangeratesapi.io/' + date + '?symbols=GBP,ILS')
    binary = response.content
    output = json.loads(str(binary, 'utf-8'))
    GBP, ILS = (output['rates']['GBP']), (output['rates']['ILS'])
    return Decimal(GBP / ILS)

print(get_exchange_rate('2019-01-22'))

