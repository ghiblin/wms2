# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0137_auto_20151029_1509'),
    ]

    operations = [
        migrations.AddField(
            model_name='bollafornitore',
            name='codice_bolla_fornitore',
            field=models.CharField(null=True, max_length=15, blank=True),
        ),
        migrations.AddField(
            model_name='bollafornitore',
            name='data_bolla_fornitore',
            field=models.DateField(null=True),
        ),
        migrations.AddField(
            model_name='rigabollafornitore',
            name='articolo_codice_fornitore',
            field=models.CharField(null=True, max_length=200, blank=True),
        ),
    ]
