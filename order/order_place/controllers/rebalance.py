import order_place.models as m
from django.db.models import F

def rebalance (user, table = None):
    invoice_data = m.Invoice.objects.filter(invoice_id__icontains=user).values(
        date=F('invoice_date'),
        name=F('invoice_id'),
        sum=F('invoice_price')
    )
    payment_data = m.Balance.objects.filter(customer_id__icontains = user).values(
        date=F('sum_date'),
        name=F('sum_payer'),
        sum=F('sum_received')
    )
    combined_data = invoice_data.union(payment_data).order_by('date')
    total = 0
    invoice = []
    
    for z in combined_data:
        if "PVZ" + user in z['name']:
            if table:
                invoice.append(z)
                obj = m.Invoice.objects.get(invoice_id = z['name'])
                obj.invoice_status = False
                obj.save()
            total -= z['sum']
        else:
            total += z['sum']
        if table:
            if total >= 0:
                if invoice:
                    for a in invoice:
                        obj = m.Invoice.objects.get(invoice_id = a['name'])
                        obj.invoice_status = True
                        obj.save()
                    invoice = []
    m.Customer.objects.filter(customer_id = user).update(customer_balance = total)                         
    return  combined_data, total             