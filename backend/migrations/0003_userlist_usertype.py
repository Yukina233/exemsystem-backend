# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2018-11-08 14:56
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0002_auto_20181027_1534'),
    ]

    operations = [
        migrations.AddField(
            model_name='userlist',
            name='usertype',
            field=models.CharField(default=1, max_length=20),
            preserve_default=False,
        ),
    ]
