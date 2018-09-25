# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0125_fatturacliente_da_confermare'),
    ]

    operations = [
        migrations.AddField(
            model_name='bollacliente',
            name='oggetto',
            field=models.CharField(blank=True, null=True, max_length=150),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='fatturacliente',
            name='oggetto',
            field=models.CharField(blank=True, null=True, max_length=150),
            preserve_default=True,
        ),
    ]
