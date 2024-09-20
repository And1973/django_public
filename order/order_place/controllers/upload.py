from django.http import HttpResponse
import requests
from OpenSSL import crypto
import base64
from urllib.parse import parse_qs
import order_place.models as m
from order_place.controllers.rebalance import rebalance as re 
from django.views.decorators.csrf import csrf_exempt



    
def send_message(chat_id, text):
    token = 'Telegram_token'
    url = f'https://api.telegram.org/bot{token}/sendMessage'
    data = {'chat_id': chat_id, 'text': text}
    requests.post(url, data=data)    

@csrf_exempt    
def test_paysera(request):
    if request.method == 'POST':
        send_message(118876845, "Post request from Paysera")
        try:
            def load_from_web():
                url = "https://www.paysera.com/download/public.key"
                response = requests.get(url)
                return crypto.load_certificate(crypto.FILETYPE_PEM, response.content)
            def verify_signature(data, signature, public_key):
                try:
                    crypto.verify(public_key, signature, data, 'sha1')
                    return True
                except crypto.Error as e :
                    send_message(118876845, f'{e}')
                    return False
            sign = request.POST.get('sign')
            data = request.POST.get('data')
            public_key = load_from_web()
            if sign and data and public_key:
                sign_replaced = sign.replace('-','+').replace('_','/')
                sign_decoded = base64.b64decode(sign_replaced)
                if verify_signature(data.encode(), sign_decoded, public_key):
                    data_replaced = data.replace('-', '+').replace('_', '/')
                    data_decoded = base64.b64decode(data_replaced)
                    params = parse_qs(data_decoded.decode('utf-8'))
                    try:
                        customer = m.Customer.objects.filter(customer_vat = "LV" + params["payer_code"]).first()
                        send_message(118876845,f'{params["payer_name"]} {params["payer_code"]} {params["amount"]} {params["details"]}')
                        if customer:
                            cust_id = customer.customer_id
                            m.Balance.objects.create(sum_received = float(params['amount']), sum_payer = customer.customer_name, sum_aim = params['details'], customer_id = cust_id )
                            re(cust_id)
                    except:
                        m.Balance.objects.create(sum_received = float(params['amount']), sum_payer = params['payer_name'], sum_aim = params['details'])
                        send_message(118876845,f'{params["payer_name"]} "No payer code" {params["amount"]} {params["details"]}')
                else:
                    send_message(118876845,f'Paysera message doesnt pass verify signature check')
            else:
                send_message(118876845, "No sign or data or public key from Paysera")
        except Exception as e:
            send_message(118876845,f'error : {e}')
        return HttpResponse('OK')