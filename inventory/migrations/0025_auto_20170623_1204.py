# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-06-23 10:04
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0024_auto_20170623_1059'),
    ]

    operations = [
        migrations.AddField(
            model_name='productmodel',
            name='all_patterns_present',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='productmodel',
            name='product_images_present',
            field=models.BooleanField(default=False),
        ),
    ]