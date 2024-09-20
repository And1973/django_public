# Generated by Django 5.0.7 on 2024-07-30 11:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order_place', '0004_user_item_given'),
    ]

    operations = [
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('customer_id', models.CharField(max_length=10)),
                ('customer_name', models.CharField(max_length=100)),
                ('customer_vat', models.CharField(max_length=10)),
                ('customer_vat_valid', models.CharField(max_length=10)),
                ('customer_email', models.EmailField(max_length=254)),
                ('customer_email_valid', models.BooleanField()),
                ('customer_address', models.CharField(max_length=200)),
                ('customer_delivery_address', models.CharField(max_length=200)),
                ('customer_phone', models.IntegerField()),
                ('customer_phone_valid', models.BooleanField()),
                ('customer_balance', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('invoice_id', models.CharField(max_length=50)),
                ('invoice_date', models.DateField()),
                ('invoice_price', models.FloatField()),
                ('invoice_status', models.BooleanField()),
                ('customer_id', models.CharField(max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_id', models.CharField(max_length=50)),
                ('order_date', models.DateField()),
                ('order_price', models.FloatField()),
                ('order_status', models.BooleanField()),
                ('customer_id', models.CharField(max_length=10)),
            ],
        ),
        migrations.AddField(
            model_name='user',
            name='user_invoice_id',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='user_order_id',
            field=models.CharField(max_length=50, null=True),
        ),
    ]
