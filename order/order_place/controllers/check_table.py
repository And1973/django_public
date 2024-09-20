import json
from django.http import JsonResponse
from order_place.models import User as u
from order_place.models import Order as o
from order_place.models import Invoice as i
from django.db.models import Max, Count, Q, OuterRef, Subquery
from order_place.controllers.rebalance import rebalance as re

rebalance_launch_count = 0

def check_table(request):
    global rebalance_launch_count
    if request.method =='POST':
        data = json.loads(request.body.decode('utf-8'))
        user = data.get('user')
        table_name = data.get('table_name')
        
        if table_name == 'table_2' and user:
            orders = o.objects.filter(order_id__icontains=user).values('order_id', 'order_date', 'order_price')
            users_subquery = u.objects.filter(user_order_id=OuterRef('order_id')).values('user_order_id').annotate(
                max_id=Max('id'),
                status=Count('id'),
                non_null_invoices=Count('user_invoice_id', filter=~Q(user_invoice_id__in=[None, '']))
            ).values('max_id', 'status', 'non_null_invoices')
            annotated_orders = orders.annotate(
                max_id=Subquery(users_subquery.values('max_id')[:1]),
                status=Subquery(users_subquery.values('status')[:1]),
                non_null_invoices=Subquery(users_subquery.values('non_null_invoices')[:1])
            ).order_by('-max_id')
            anno = []
            for abi in annotated_orders:
                anno.append({
                    'order_id' : abi['order_id'],
                    'order_date' : abi['order_date'].strftime('%Y-%m-%d %H:%M:%S'),
                    'order_price' : abi['order_price'],
                    'status' : -1 if abi['status']-abi['non_null_invoices'] == abi['status'] else 0 if abi['status']-abi['non_null_invoices'] > 0 else 1
                })
            return JsonResponse( {'orders': anno} )
     
        if table_name == 'table_3' and user or table_name == 'table_3_no_rebalance' and user:
            if table_name == 'table_3':
                re(user, table_name)
            invoices = i.objects.filter( invoice_id__icontains=user ).order_by('invoice_date')
            invoice_list = []
            for au in reversed(invoices):
                invoice_list.append({
                    'invoice_id': au.invoice_id,
                    'invoice_date': au.invoice_date.strftime('%Y-%m-%d %H:%M:%S'),
                    'invoice_price': au.invoice_price,
                    'invoice_status': au.invoice_status,
                    'invoice_url':au.invoice.url if au.invoice else ""
                })
            return JsonResponse( {'invoice': invoice_list} )

        if table_name == 'table_5' and user or table_name == 'table_5_no_rebalance' and user:
            if table_name == 'table_5':
                combined_data, total = re(user, table_name)
            else:
                combined_data, total = re(user)    
            return JsonResponse( {'balance': {'balance': list(reversed(combined_data)), 'total':total}} )