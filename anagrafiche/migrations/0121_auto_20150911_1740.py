# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0120_auto_20150911_1546'),
    ]

    operations = [
        migrations.AddField(
            model_name='fatturacliente',
            name='totale',
            field=models.DecimalField(default=0, decimal_places=2, max_digits=9),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='ordinecliente',
            name='fatturato',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='rigaordinecliente',
            name='fatturata',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
