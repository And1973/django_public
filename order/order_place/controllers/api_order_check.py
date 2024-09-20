from django.http import JsonResponse
from order_place.models import User as u
from order_place.controllers.timer import make_orders as mo 
import httpx
from asgiref.sync import sync_to_async


TOKEN                  = "Supplier_token"
VPRN		           = 'VPRN'


main_params  = {
    'vpnr': VPRN,
    'authcode': TOKEN
}

async def check(request):
    if request.method =='GET':
        order_id = request.GET.get('order_id', None)
        if order_id:
            async with httpx.AsyncClient() as c:
                response = await c.get("Supliers_URL" + order_id, params = main_params )
                if response.is_success:
                    datas = response.json()
                    editable = datas["editable"]
                    if editable:
                        return JsonResponse({'info':'order editable', 'editable':True, 'old_items_outdated': False} )
                    else:
                        await sync_to_async(mo)()
                        return JsonResponse({'info':'order not editable', 'editable':False, 'old_items_outdated': True})
                else:
                    await sync_to_async(mo)() 
                    return JsonResponse({'info': 'order not existing','answer':f' Suppliers API response {order_id}{response.json()}','editable':False, 'old_items_outdated': True} )        
        return JsonResponse({'error': f'order id bad {order_id}'}, status=400)
    return JsonResponse({'error': 'не GET запрос '}, status=400)
