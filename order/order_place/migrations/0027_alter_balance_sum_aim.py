# Generated by Django 5.0.7 on 2024-08-28 17:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order_place', '0026_alter_balance_sum_aim'),
    ]

    operations = [
        migrations.AlterField(
            model_name='balance',
            name='sum_aim',
            field=models.CharField(max_length=100, null=True),
        ),
    ]
