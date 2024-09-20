from django.http import JsonResponse
import httpx


TOKEN                  = "Supplier_token"
VPRN		           = 'VPRN'


main_params  = {
    'vpnr': VPRN,
    'authcode': TOKEN
}

async def check(request):
    if request.method =='GET':
        id = request.GET.get('id', None)
        quantity = request.GET.get('quantity', None)
        if id and quantity:
            async with httpx.AsyncClient() as c:
                main_params['artnr'] = id
                main_params['quantity'] = quantity
                response = await c.get("Supliers_URL", params=main_params)
                if response.is_success:
                    stock = response.json()
                    if stock['stock_available']:
                        return JsonResponse({'available': True})
                    else:
                        return JsonResponse({'available': False})
                else:
                    return JsonResponse({'error':f'{response.json}'}, status=400)   
        return JsonResponse({'error': 'недостаточно данных для запроса'}, status=400)
    return JsonResponse({'error': 'не GET запрос '}, status=400)



