import order_place.models as m
from datetime import date
from django.db.models import Sum, F
from django.contrib.auth.models import User

def make_orders():
    existing_orders = m.Order.objects.values('order_id')
    existing_orders = [i['order_id'] for i in existing_orders ]
    users = User.objects.all()
    for user in users:
        items_true  = m.User.objects.filter(user_id = user.username, order_status = True)
        if items_true:
            orders = items_true.values('user_id').annotate( total = Sum(F('item_price')*F('item_qty'))) 
            for item in items_true:
                same_date = [i for i in existing_orders if 'r' + item.user_id + date.today().strftime("%d%m%Y") in i ]
                if same_date:
                    item.user_order_id = 'r' + item.user_id + date.today().strftime("%d%m%Y") + '-' + str(len(same_date)+1)
                else:
                    item.user_order_id = 'r' + item.user_id + date.today().strftime("%d%m%Y") + '-1'
                item.order_status = False
            for order in orders:
                if order['user_id'] not in existing_orders:
                    m.Order.objects.create(order_id = item.user_order_id, order_date = date.today(), order_price= order['total'], order_status = -1 )
            for item in items_true:
                item.save()