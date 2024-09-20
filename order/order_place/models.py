from django.db import models
import pusher
from django.db import transaction

pusher_client = pusher.Pusher(
  app_id='app_id',
  key='key',
  secret='secret',
  cluster='eu',
  ssl=True
)

class User(models.Model):
    item_id         = models.CharField(max_length=50)              # phone code unique
    item_name       = models.CharField(max_length=200)             # phone name
    item_qty        = models.IntegerField()                        # qty ordered
    item_price      = models.FloatField()                          # price of an item
    order_id        = models.IntegerField()                        # order code 
    order_status    = models.BooleanField(null=True)               # item order status outdated or actual 
    user_id         = models.CharField(max_length=10)              # user coordinatly to authorization page 
    item_given      = models.BooleanField(null=True)
    user_order_id   = models.CharField(max_length=50, null=True, blank=True)         
    user_invoice_id = models.CharField(max_length=50, null=True, blank=True)
    def order_status_display(self):
        return "Actual" if self.order_status else 'Outdated'
    order_status_display.short_description = 'Order Status'
    def save(self, *args, **kwargs):
        with transaction.atomic():
            super().save(*args, **kwargs)
        pusher_client.trigger('1857061', 'message', {'message': 'table_1'})

    def delete(self, *args, **kwargs):
        with transaction.atomic():
            pusher_client.trigger('1857061', 'message', {'message': 'table_1'})
        super().delete(*args, **kwargs)
    
class Order(models.Model):
    order_id     = models.CharField(max_length=50)            # order nr unique 
    order_date   = models.DateField()                         # order date
    order_price  = models.FloatField()                        # order total price
    order_status = models.IntegerField()                      # order status in progress ,partial or full
    def order_status_display(self):
        return "In Progress" if self.order_status ==-1 else 'Partial' if self.order_status==0 else 'Full'
    order_status_display.short_description = 'Order Status'
    def order_price_display(self):
        return round(self.order_price, 2)
    order_status_display.short_description = 'Order Price'
    def save(self, *args, **kwargs):
        with transaction.atomic():
            super().save(*args, **kwargs)
        pusher_client.trigger('1857061', 'message', {'message': 'table_2'})

    def delete(self, *args, **kwargs):
        with transaction.atomic():
            pusher_client.trigger('1857061', 'message', {'message': 'table_2'})
        super().delete(*args, **kwargs)

class Invoice(models.Model):
    invoice_id     = models.CharField(max_length=50)           # invoice nr unique 
    invoice_date   = models.DateTimeField()                        # invoice date
    invoice_price  = models.FloatField()                       # invoice total price 
    invoice_status = models.BooleanField()                     # invoice status paid or unpaid
    invoice        = models.FileField(upload_to='uploads/',  null=True, blank=True)
    def invoice_status_display(self):
        return "Paid" if self.invoice_status else "Unpaid"
    invoice_status_display.short_description = 'Invoice Status'
    
    def save(self, *args, **kwargs):
        modified_in_admin = kwargs.pop('modified_in_admin', False)
        if modified_in_admin:
            with transaction.atomic():
                super().save(*args, **kwargs)
            pusher_client.trigger('1857061', 'message', {'message': 'table_3'})
        else:
            super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        with transaction.atomic():
            super().delete(*args, **kwargs)
        pusher_client.trigger('1857061', 'message', {'message': 'table_3'})

class Customer(models.Model):
    customer_id               =  models.CharField(max_length=10)
    customer_name             =  models.CharField(max_length=100)
    customer_vat              =  models.CharField(max_length=15)
    customer_vat_valid        =  models.BooleanField() 
    customer_email            =  models.EmailField()
    customer_email_valid      =  models.BooleanField() 
    customer_address          =  models.CharField(max_length=200)
    customer_delivery_address =  models.CharField(max_length=200)
    customer_phone            =  models.CharField(max_length=15)
    customer_phone_valid      =  models.BooleanField() 
    customer_balance          =  models.FloatField(null=True, blank=True)
    
    def save(self, *args, **kwargs):
        with transaction.atomic():
            super().save(*args, **kwargs)
        pusher_client.trigger('1857061', 'message', {'message': 'table_4'})

    def delete(self, *args, **kwargs):
        with transaction.atomic():
            super().delete(*args, **kwargs)
        pusher_client.trigger('1857061', 'message', {'message': 'table_4'})

class Balance(models.Model):
    sum_received    =  models.FloatField()
    sum_date        =  models.DateTimeField(auto_now_add=True)
    sum_payer       =  models.CharField(max_length=100)
    sum_aim         =  models.CharField(max_length=100, null=True)
    customer_id     =  models.CharField(max_length=10, null=True, blank=True)
    
    def save(self, *args, **kwargs):
        with transaction.atomic():
            super().save(*args, **kwargs)
        pusher_client.trigger('1857061', 'message', {'message': 'table_5'})

    def delete(self, *args, **kwargs):
        with transaction.atomic():
            super().delete(*args, **kwargs)
        pusher_client.trigger('1857061', 'message', {'message': 'table_5'})       
    




    

    

