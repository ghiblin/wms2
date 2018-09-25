# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0165_ordinecliente_riferimento_cliente'),
    ]

    operations = [
        migrations.AddField(
            model_name='bollacliente',
            name='riferimento_cliente',
            field=models.CharField(blank=True, null=True, max_length=150, default=''),
        ),
        migrations.AddField(
            model_name='fatturacliente',
            name='riferimento_cliente',
            field=models.CharField(blank=True, null=True, max_length=150, default=''),
        ),
    ]
