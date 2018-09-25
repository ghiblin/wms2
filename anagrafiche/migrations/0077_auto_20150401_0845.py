# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0076_auto_20150401_0843'),
    ]

    operations = [
        migrations.AddField(
            model_name='dipendente',
            name='attivo',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='dipendente',
            name='codice_fiscale',
            field=models.CharField(null=True, max_length=16, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='dipendente',
            name='data_assunzione',
            field=models.DateField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='dipendente',
            name='data_cessazione',
            field=models.DateField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='dipendente',
            name='scadenza_visita_medica',
            field=models.DateField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
