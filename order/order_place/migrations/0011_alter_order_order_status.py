# Generated by Django 5.0.7 on 2024-08-06 11:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order_place', '0010_rename_sum_recieved_balance_sum_received'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='order_status',
            field=models.IntegerField(),
        ),
    ]
