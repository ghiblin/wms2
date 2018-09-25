# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0127_fatturacliente_pagamento'),
    ]

    operations = [
        migrations.AddField(
            model_name='fatturacliente',
            name='destinazione',
            field=models.ForeignKey(null=True, blank=True, to='anagrafiche.Indirizzo'),
            preserve_default=True,
        ),
    ]
