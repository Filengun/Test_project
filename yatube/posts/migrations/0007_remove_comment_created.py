# Generated by Django 2.2.16 on 2022-08-30 16:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0006_auto_20220830_1920'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='comment',
            name='created',
        ),
    ]
