# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-12-27 11:18
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('terkeph', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='phuser',
            name='latlng',
            field=models.CharField(blank=True, max_length=20),
        ),
    ]
