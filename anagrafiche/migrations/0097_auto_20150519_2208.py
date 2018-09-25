# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0096_auto_20150519_2204'),
    ]

    operations = [
        migrations.AddField(
            model_name='ordinecliente',
            name='classe_di_esecuzione',
            field=models.CharField(default='', blank=True, max_length=100),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='ordinecliente',
            name='spessori',
            field=models.CharField(default='', blank=True, max_length=100),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='ordinecliente',
            name='tipo_di_acciaio',
            field=models.CharField(default='', blank=True, max_length=100),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='ordinecliente',
            name='verniciatura',
            field=models.CharField(default='', blank=True, max_length=100),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='ordinecliente',
            name='wps',
            field=models.CharField(default='', blank=True, max_length=100),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='ordinecliente',
            name='zincatura',
            field=models.CharField(default='', blank=True, max_length=100),
            preserve_default=True,
        ),
    ]
