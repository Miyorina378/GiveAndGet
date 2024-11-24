# Generated by Django 5.1.1 on 2024-11-24 14:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users_app', '0003_report'),
    ]

    operations = [
        migrations.AlterField(
            model_name='report',
            name='reason',
            field=models.CharField(choices=[('User is spamming or harassment', 'User is spamming or harassment'), ('This user is a bot', 'This user is a bot'), ('This Product is not delivered on time', 'This Product is not delivered on time'), ('Posting copyrighted product', 'Posting copyrighted product'), ('Posting illegal product', 'Posting illegal product')], max_length=60),
        ),
    ]