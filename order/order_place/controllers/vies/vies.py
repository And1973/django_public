import requests
import django
import os
import sys
sys.path.append('Q:/Wholesale/order')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'order.settings')  
django.setup()
import order_place.models as m
from viesapi import *
import time

def send_message(chat_id, text):
    token = 'telegram_token'
    url = f'https://api.telegram.org/bot{token}/sendMessage'
    data = {'chat_id': chat_id, 'text': text}
    requests.post(url, data=data)

id = 'id'
key = 'key'
viesapi = VIESAPIClient(id, key)
vats = m.Customer.objects.values_list('customer_vat')
count = 0
for vat in vats:
    #account = viesapi.get_account_status()
    vies = viesapi.get_vies_data(vat[0])
    if vies:
        obj = m.Customer.objects.get(customer_vat = vat[0])
        if vies.valid:
            if not obj.customer_vat_valid:
                obj.customer_vat_valid = True
                obj.save()
                count +=1
                send_message(118876845, f'{obj.customer_name}  {obj.customer_id} VAT becomes valid' )
              
        else:
            if obj.customer_vat_valid:
                obj.customer_vat_valid = False
                obj.save()
                count+=1
                send_message(118876845, f'{obj.customer_name}  {obj.customer_id} VAT becomes invalid' )

    # else:
    #     print('Error: ' + viesapi.get_last_error() + ' (code: ' + str(viesapi.get_last_error_code()) + ')')
    time.sleep(1)
if count == 0:
        send_message(118876845, 'No changes with VATs')

