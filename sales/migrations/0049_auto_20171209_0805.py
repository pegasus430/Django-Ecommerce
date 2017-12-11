# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-12-09 07:05
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0048_auto_20171206_1528'),
    ]

    operations = [
        migrations.DeleteModel(
            name='PriceList',
        ),
        migrations.RemoveField(
            model_name='pricelistitem',
            name='price_list',
        ),
        migrations.RemoveField(
            model_name='pricelistitem',
            name='product',
        ),
        migrations.RemoveField(
            model_name='pricetransport',
            name='price_list',
        ),
        migrations.AlterField(
            model_name='pricelistassignment',
            name='price_list',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='pricelists.PriceList'),
        ),
        migrations.AlterField(
            model_name='salesorder',
            name='price_list',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='pricelists.PriceList'),
        ),
        migrations.AlterField(
            model_name='salesorderproduct',
            name='price_list_item',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='pricelists.PriceListItem'),
        ),
        migrations.DeleteModel(
            name='PriceListItem',
        ),
        migrations.DeleteModel(
            name='PriceTransport',
        ),
    ]