# Generated by Django 5.0.1 on 2024-04-26 04:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order_place', '0003_delete_user_1_delete_user_2_delete_user_3'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='item_given',
            field=models.BooleanField(null=True),
        ),
    ]
