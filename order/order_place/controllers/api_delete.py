
from django.http import JsonResponse
from django.contrib.auth.models import User
from order_place.models import User as m
from asgiref.sync import sync_to_async
import httpx
from django.db.models import Sum, F

import logging

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

logger = logging.getLogger('myapp')

async def send_message(c, chat_id, text):
    token = 'Telegram_token'
    url = f'https://api.telegram.org/bot{token}/sendMessage'
    data = {'chat_id': chat_id, 'text': text}
    await c.post(url, data=data)
    
async def delete(request):
    if request.method =='DELETE':
        id = request.GET.get('id', None)
        order_id = request.GET.get('order_id', None)
        
        if id:
            current_user_id = await sync_to_async(request.session.get)('user')
            user_name = await User.objects.aget(id=current_user_id)
            user = await m.objects.filter(order_id = order_id, order_status = True).acount()
            async with httpx.AsyncClient() as c:
                if user == 1:
                    response = await c.get("Supliers_URL" + order_id, params=main_params)
                    if response.is_success:
                        response = await c.delete("Supliers_URL" + order_id, params = main_params )
                        if response.is_success:
                            item = await m.objects.aget(item_id = id, order_id= order_id, user_id=user_name,order_status = True)
                            await item.adelete()
                            await send_message(c, 118876845, f'{user_name} deleted:\n{item.item_name}\nБД пустая , заказ удален')
                            return JsonResponse({'success': ' БД пустая , заказ удален'})
                        else:
                            return JsonResponse({'message': f'{order_id}  ошибка удаления заказа на внешнем API {response }'}, status = 400)
                    else:
                        return JsonResponse({'message': f' {order_id}  ошибка блокировки заказа на внешнем API {response}'}, status = 400)
                else:
                    item = await m.objects.aget(item_id = id, user_id = user_name, order_id= order_id, order_status = True)
                    await item.adelete()
                    aggregated_data = (m.objects.filter(order_status = True, order_id = order_id 
                    ).values( article_number = F('item_id')
                    ).annotate( requested_stock=Sum('item_qty')
                    ).order_by('item_id' ))
                    items = [ i async for i in aggregated_data ]
                    load['items'] = items
                    response = await c.get("Supliers_URL"  + order_id, params=main_params)
                    if response.is_success:
                        response = await c.put("Supliers_URL" + order_id, params=main_params, json = load)
                        if response.is_success:
                            await send_message(c, 118876845, f'{user_name} deleted:\n{item.item_name}')
                            return JsonResponse({'error': 'Элемент найден и удален'}, status=200)
                        else:
                            return JsonResponse({'message': f'ошибка удаления заказа на внешнем API {response}'})
                    else:
                        return JsonResponse({'message': f'ошибка блокировки  заказа на внешнем API {response}'}) 
        return JsonResponse({'error': 'No id found'}, status = 400)
    return JsonResponse({'error': 'Not DELETE'}, status = 400)  