# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-12-27 11:20
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('terkeph', '0002_phuser_latlng'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='phuser',
            name='point_lat',
        ),
        migrations.RemoveField(
            model_name='phuser',
            name='point_lng',
        ),
    ]
