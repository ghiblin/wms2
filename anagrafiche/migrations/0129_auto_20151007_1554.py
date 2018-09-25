# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0128_fatturacliente_destinazione'),
    ]

    operations = [
        migrations.AddField(
            model_name='fatturacliente',
            name='sconto_euro',
            field=models.DecimalField(default=0, max_digits=12, decimal_places=2),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='fatturacliente',
            name='sconto_percentuale',
            field=models.DecimalField(default=0, max_digits=6, decimal_places=2),
            preserve_default=True,
        ),
    ]
