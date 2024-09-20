import json
from django.http import JsonResponse
from django.contrib.auth.models import User
from order_place.models import User as m
from django.db.models import Sum, F
from asgiref.sync import sync_to_async
import httpx

import logging

logger = logging.getLogger('myapp')

TOKEN                  = "Supplier_token"
VPRN		           = 'VPRN'
ADDRESS                =  'Address'

main_params  = {
    'vpnr': VPRN,
    'authcode': TOKEN
}

headers = {
    'Accept': 'application/json'
}

load = {
    "customer_address_id": ADDRESS,
    "customer_reference": "-"
}

async def send_message(c, chat_id, text):
    token = 'Telegram_token'
    url = f'https://api.telegram.org/bot{token}/sendMessage'
    data = {'chat_id': chat_id, 'text': text}
    await c.post(url, data=data)
    
async def create(request):
    if request.method =='POST':
        data = json.loads(request.body.decode('utf-8'))
        id = data.get('id')
        name = data.get('name')
        price = data.get('price')
        qty = data.get('qty')
        async with httpx.AsyncClient() as c:
            if id and name and price and qty:
                current_user_id = await sync_to_async(request.session.get)('user')
                user_name = await User.objects.aget(id=current_user_id)
                exist = await m.objects.filter(order_status = True).aexists()
                if exist:
                    last_item = await m.objects.alast()
                    order_id = str(last_item.order_id)
                    url = "Supliers_URL"+ order_id
                    if last_item:
                        await send_message(c, 118876845, f'{last_item.order_id}')
                    else:
                        await send_message(c, 118876845, f'last_item and order_id are None')
                    response = await c.get(url, params = main_params )
                    if response.is_success:
                        datas = response.json()
                        editable = datas["editable"]
                        if editable:
                            order = m(item_id = id, item_name = name , item_qty = qty, item_price = price, order_id = order_id, order_status = True, user_id = user_name)
                            await order.asave()
                            aggregated_data = m.objects.filter(order_status = True, order_id = order_id
                            ).values( article_number = F('item_id')
                            ).annotate( requested_stock=Sum('item_qty')
                            ).order_by('item_id' )
                            items = [ i async for i in aggregated_data ]
                            load['items'] = items
                            response = await c.get("Supliers_URL"  + order_id, params=main_params)
                            if response.is_success:
                                response = await c.put("Supliers_URL" + order_id, params=main_params, json = load)
                                if response.is_success:
                                    await send_message(c, 118876845, f'{user_name} ordered:\n{name }\n{qty} шт.')
                                    return JsonResponse( {'success':f'Получен элемент и сохранен в базе данных','order_id':order_id, 'old_items_outdated':False} )    
                                else:
                                    return JsonResponse({'error': 'ошибка создания заказа на внешнем API'}, status = 400)
                            else:
                                return JsonResponse({'error': 'ошибка блокирования заказа на внешнем API'}, status = 400)
                
                items = []
                item = {
                    "article_number" : id,
                    "requested_stock": qty
                }
                items.append(item)
                load['items'] = items
                response = await c.post("Supliers_URL", params = main_params, json = load)
                if response.is_success:
                    datas = response.json()
                    order_id = datas['order_id']
                    order = m(item_id = id, item_name = name , item_qty = qty, item_price = price, order_id = order_id, order_status = True, user_id = user_name)
                    await order.asave()
                    await send_message(c, 118876845, f'New order created\n{user_name} ordered:\n{name}\n{qty} шт.\n')
                    return JsonResponse( {'success': f'Order create for first item in DB', 'order_id': order_id })
                else:
                    return JsonResponse({'error': 'ошибка создания заказа на внешнем API'}, status= 400)
    
