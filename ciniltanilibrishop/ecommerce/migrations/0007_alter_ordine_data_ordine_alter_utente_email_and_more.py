# Generated by Django 5.2 on 2025-05-14 06:43

import datetime
import django.contrib.auth.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecommerce', '0006_alter_ordine_data_ordine_carrello'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ordine',
            name='data_ordine',
            field=models.DateTimeField(default=datetime.datetime(2025, 5, 14, 8, 43, 4, 208873, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='utente',
            name='email',
            field=models.EmailField(blank=True, max_length=254, verbose_name='email address'),
        ),
        migrations.AlterField(
            model_name='utente',
            name='username',
            field=models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username'),
        ),
    ]
