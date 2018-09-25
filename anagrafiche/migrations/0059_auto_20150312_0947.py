# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0058_auto_20150312_0940'),
    ]

    operations = [
        migrations.AddField(
            model_name='rigaordinecliente',
            name='articolo_descrizione',
            field=models.CharField(default='', max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='rigaordinecliente',
            name='articolo_prezzo',
            field=models.DecimalField(default=5, decimal_places=2, max_digits=7),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='rigaordinecliente',
            name='note',
            field=models.CharField(default='', blank=True, max_length=200),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='rigapreventivocliente',
            name='articolo_descrizione',
            field=models.CharField(max_length=100),
        ),
    ]
