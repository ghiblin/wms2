# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0008_cliente_partita_iva'),
    ]

    operations = [
        migrations.AddField(
            model_name='commessa',
            name='data_apertura',
            field=models.DateField(default='2015-01-01'),
            preserve_default=True,
        ),
    ]
