# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0136_auto_20151014_1133'),
    ]

    operations = [
        migrations.AddField(
            model_name='ordinefornitore',
            name='codice_ordine_fornitore',
            field=models.CharField(max_length=15, blank=True, null=True),
        ),
        migrations.AddField(
            model_name='ordinefornitore',
            name='data_ordine_fornitore',
            field=models.DateField(null=True),
        ),
        migrations.AddField(
            model_name='rigaordinefornitore',
            name='articolo_codice_fornitore',
            field=models.CharField(max_length=200, blank=True, null=True),
        ),
        migrations.AddField(
            model_name='rigaordinefornitore',
            name='data_consegna',
            field=models.DateField(null=True),
        ),
    ]
