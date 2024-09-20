import json
from django.http import JsonResponse
from order_place.models import User as u

def modal(request):
    if request.method =='POST':
        data = json.loads(request.body.decode('utf-8'))
        id = data.get('id')
        table_name = data.get('table_name')
        if table_name == 'order':
            items = u.objects.filter(user_order_id=id)
            if items:
                items_list = []
                for item in items:
                    items_list.append([item.item_name,item.item_qty, item.item_price])
                return JsonResponse({'qty': True, 'items_list':items_list} )
    return JsonResponse({'error': 'modal window error'}, status=400)