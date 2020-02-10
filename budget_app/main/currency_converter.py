from decimal import *
import requests
import json

def currency_converter(currency_1, currency_2, date):
    """ Calculates exchange rate from currency_2 to currency_1
    on the specified date. Based on European Central Bank """
    response = requests.get(
        'https://api.exchangeratesapi.io/' + str(date) +
        '?symbols=' + currency_1 + ',' + currency_2)
    output = json.loads(response.content)
    return Decimal(output['rates'][currency_1] / output['rates'][currency_2])
