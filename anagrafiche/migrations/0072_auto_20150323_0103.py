# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0071_preventivocliente_totale'),
    ]

    operations = [
        migrations.AddField(
            model_name='contocorrente',
            name='swift',
            field=models.CharField(null=True, blank=True, max_length=11),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='ordinecliente',
            name='totale',
            field=models.DecimalField(max_digits=8, default=0, decimal_places=2),
            preserve_default=True,
        ),
    ]
