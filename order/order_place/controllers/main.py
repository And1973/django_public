from django.shortcuts import render
import order_place.models as m
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
import csv
import requests
from io import StringIO
import diskcache as dc
from django.conf import settings

cache = dc.Cache(str(settings.BASE_DIR / 'cache'))

def send_message(chat_id, text):
    token = 'Telegram_token'
    url = f'https://api.telegram.org/bot{token}/sendMessage'
    data = {'chat_id': chat_id, 'text': text}
    requests.post(url, data=data)

@login_required
def order_page(request):
    url = ("Suppliers_url")
    
    def fetch_and_parse_csv(url):
        response = requests.get(url)
        if response.status_code == 200:
            content = StringIO(response.content.decode('utf-8'))
            csv_reader = csv.reader(content)
            datas = list(csv_reader)
            return datas
        return None

    def get_data(url):
        cached_data = cache.get(url)
        if cached_data:
            send_message(118876845, f"CSV fetched from the cache.")
            return cached_data
        else:
            send_message(118876845, f"CSV fetched from the network.")
            data = fetch_and_parse_csv(url)
            if data:
                cache.set(url, data, expire = 3600)
            return data

    datas = get_data(url)    

    phones = []
    if datas:
        for item in datas[1:]:
            if item[2] != '0':
                format = lambda nr: "{:.2f}".format(float(nr)*1.12)
                phones.append(['id-'+item[0], item[1], item[2], format(item[3])])
    
    data = {"phones":phones}
    current_user_id = request.session.get('user')
    user_name = User.objects.get(id=current_user_id)
    orders = m.User.objects.filter(user_id = user_name, order_status = True)
    item_qty = lambda it : next(( i[2] for i in phones if i[0] == it), None)
    orders = list(
        map(
            lambda order: {
                'item_id'    : 'id-'+ order.item_id, 
                'item_name'  : order.item_name, 
                'item_qty'   : order.item_qty,
                'item_price' : order.item_price,
                'item_total_qty'   :  item_qty(order.item_id) if item_qty(order.item_id) is not None else order.item_qty,
                'item_total_price' : "{:.2f}".format(float(order.item_price) * order.item_qty),
                'order_id'   : order.order_id,
                'order_status' :  order.order_status,
                'item_given' : order.item_given
            },
            orders
        )
    )

    customer = m.Customer.objects.get( customer_id = user_name )
    data = {"phones":phones, "orders":orders,'cust':customer}
    return render(request, "order.html", data)
    