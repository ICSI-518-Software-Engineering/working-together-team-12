# Generated by Django 5.0.2 on 2024-03-26 11:21

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0012_alter_paymentdetail_card_holder_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='cityselection',
            name='created',
            field=models.DateField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]