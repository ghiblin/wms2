# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0138_auto_20151105_1908'),
    ]

    operations = [
        migrations.AddField(
            model_name='fatturafornitore',
            name='codice_fattura_fornitore',
            field=models.CharField(blank=True, null=True, max_length=15),
        ),
        migrations.AddField(
            model_name='fatturafornitore',
            name='data_fattura_fornitore',
            field=models.DateField(null=True),
        ),
        migrations.AddField(
            model_name='rigafatturafornitore',
            name='articolo_codice_fornitore',
            field=models.CharField(blank=True, null=True, max_length=200),
        ),
    ]
