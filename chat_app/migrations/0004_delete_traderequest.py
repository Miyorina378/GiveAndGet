# Generated by Django 5.1.1 on 2024-12-17 15:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('chat_app', '0003_traderequest'),
    ]

    operations = [
        migrations.DeleteModel(
            name='TradeRequest',
        ),
    ]