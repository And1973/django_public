from django.contrib import admin
from .models import User, Order, Invoice, Customer, Balance
from django.utils.safestring import mark_safe
from django.db.models import Max

class UserOrderIDFilter(admin.SimpleListFilter):
    title = 'User Order ID'
    parameter_name = 'user_order_id'

    def lookups(self, request, model_admin):
        user_order_ids = User.objects.values_list('user_order_id', flat=True).annotate(max_id=Max('id')).order_by('-max_id')
        return [(user_order_id, user_order_id) for user_order_id in user_order_ids]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(user_order_id=self.value())
        return queryset

class UserAdmin(admin.ModelAdmin):
    list_display = ('item_id', 'item_name', 'item_qty', 'item_price', 'order_id', 'order_status_display', 'user_id','user_invoice_id', 'user_order_id')
    list_filter  =  (UserOrderIDFilter,)
    list_editable = ('user_invoice_id',)
    # search_fields = ('item_qty','item_price')
admin.site.register(User, UserAdmin)

class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'order_date', 'order_price_display', 'order_status_display')
    def order_price_display(self, obj):
        return mark_safe(f'<div style="width: 80px; text-align: right;">{round(obj.order_price, 2):.2f}<span>€</span></div>')
    order_price_display.short_description = 'Order Price'
admin.site.register(Order, OrderAdmin)

class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_id', 'invoice_date', 'invoice_price', 'invoice_status_display','invoice')
    list_editable = ('invoice',) 
    def save_model(self, request, obj, form, change):
        obj.save(modified_in_admin=True)
admin.site.register(Invoice, InvoiceAdmin)

class CustomerAdmin(admin.ModelAdmin):
    list_display = ('customer_id', 'customer_name', 'customer_vat', 'customer_vat_valid','customer_email','customer_email_valid','customer_address','customer_delivery_address','customer_phone','customer_phone_valid','customer_balance') 
admin.site.register(Customer, CustomerAdmin)

class BalanceAdmin(admin.ModelAdmin):
    list_display = ('sum_received', 'sum_date', 'sum_payer','customer_id') 
admin.site.register(Balance, BalanceAdmin)