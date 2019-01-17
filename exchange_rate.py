import requests
import json

response = requests.get(
        'https://api.exchangeratesapi.io/latest?symbols=GBP,ILS')

binary = response.content
output = json.loads(str(binary, 'utf-8'))

GBP = (output['rates']['GBP'])
ILS = (output['rates']['ILS'])

rate = GBP / ILS

print(rate)

