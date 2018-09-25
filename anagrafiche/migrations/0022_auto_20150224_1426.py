# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0021_auto_20150224_1418'),
    ]

    operations = [
        migrations.AddField(
            model_name='cliente',
            name='codice',
            field=models.CharField(max_length=30, default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='cliente',
            name='codice_fiscale',
            field=models.CharField(max_length=16, blank=True, null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='cliente',
            name='partita_iva',
            field=models.CharField(max_length=12, default='', blank=True, null=True),
        ),
    ]
