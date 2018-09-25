# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0113_bollacliente_vettore'),
    ]

    operations = [
        migrations.AddField(
            model_name='ordinecliente',
            name='sconto_euro',
            field=models.DecimalField(default=0, decimal_places=2, max_digits=9),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='ordinecliente',
            name='sconto_percentuale',
            field=models.DecimalField(default=0, decimal_places=2, max_digits=5),
            preserve_default=True,
        ),
    ]
