# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2018-05-24 17:17
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organization', '0008_auto_20170418_2339'),
    ]

    operations = [
        migrations.AlterField(
            model_name='teacher',
            name='age',
            field=models.IntegerField(default=30, max_length=100, verbose_name='年龄'),
        ),
        migrations.AlterField(
            model_name='teacher',
            name='work_years',
            field=models.IntegerField(default=0, max_length=60, verbose_name='工作年限'),
        ),
    ]
