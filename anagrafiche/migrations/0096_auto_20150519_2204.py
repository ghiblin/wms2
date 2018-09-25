# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0095_auto_20150516_1730'),
    ]

    operations = [
        migrations.AddField(
            model_name='preventivocliente',
            name='classe_di_esecuzione',
            field=models.CharField(blank=True, max_length=100, default=''),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='preventivocliente',
            name='spessori',
            field=models.CharField(blank=True, max_length=100, default=''),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='preventivocliente',
            name='tipo_di_acciaio',
            field=models.CharField(blank=True, max_length=100, default=''),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='preventivocliente',
            name='verniciatura',
            field=models.CharField(blank=True, max_length=100, default=''),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='preventivocliente',
            name='wps',
            field=models.CharField(blank=True, max_length=100, default=''),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='preventivocliente',
            name='zincatura',
            field=models.CharField(blank=True, max_length=100, default=''),
            preserve_default=True,
        ),
    ]
