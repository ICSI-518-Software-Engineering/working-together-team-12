# Generated by Django 5.0.4 on 2024-04-19 23:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0020_airportlocid'),
    ]

    operations = [
        migrations.RenameField(
            model_name='airportlocid',
            old_name='cid',
            new_name='locid',
        ),
    ]