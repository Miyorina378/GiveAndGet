# Generated by Django 5.1.1 on 2024-12-17 16:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_meetingpoint_seller_name_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='meetingpoint',
            name='seller_name',
            field=models.CharField(default='', max_length=100),
        ),
    ]
