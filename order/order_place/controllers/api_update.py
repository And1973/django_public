import requests
from django.http import JsonResponse
from django.contrib.auth.models import User
from order_place.models import User as u
from django.db.models import Sum, F
from asgiref.sync import sync_to_async
import httpx

import logging

logger = logging.getLogger('myapp')

TOKEN                  = "Supplier_token"
VPRN		           = 'VPRN'

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


async def update(request):
    if request.method =='PUT':
        id = request.GET.get('id', None)
        quantity = request.GET.get('quantity', None)
        order_id = request.GET.get('order_id', None)
        if id and quantity and order_id :
            async with httpx.AsyncClient() as c:
                current_user_id = await sync_to_async(request.session.get)('user')
                user_name  = await User.objects.aget(id=current_user_id)
                await u.objects.filter(user_id=user_name, item_id = id, order_id = order_id, order_status = True).aupdate(item_qty = quantity)
                item = await u.objects.aget(user_id=user_name, item_id = id, order_id = order_id, order_status = True)
                aggregated_data = u.objects.filter(order_status = True, order_id = order_id 
                ).values( article_number = F('item_id')
                ).annotate( requested_stock=Sum('item_qty')
                ).order_by('item_id' )
                items = [ i async for i in aggregated_data ]
                load['items'] = items
                response = await c.get("Supliers_URL"  + order_id, params=main_params)
                if response.is_success:
                    response = await c.put("Supliers_URL" + order_id, params=main_params, json = load)
                    if response.is_success:
                        await send_message(c, 118876845, f'{user_name} updated:\n{item.item_name}\nна {quantity} шт.')
                        return JsonResponse({'error': f'Элемент найден и отредактирован{item}'}, status=200)            
                    else:
                        return JsonResponse({'message': f'ошибка редактирования заказа на внешнем API'})
    return JsonResponse({'error': f'Bad request {id}  {order_id} {quantity}'}, status=400)
