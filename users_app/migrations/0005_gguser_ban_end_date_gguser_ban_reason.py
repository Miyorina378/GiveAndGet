# Generated by Django 5.1.1 on 2024-12-15 04:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users_app', '0004_alter_report_reason'),
    ]

    operations = [
        migrations.AddField(
            model_name='gguser',
            name='ban_end_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='gguser',
            name='ban_reason',
            field=models.TextField(blank=True, null=True),
        ),
    ]
