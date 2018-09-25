# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0109_auto_20150714_1206'),
    ]

    operations = [
        migrations.AddField(
            model_name='bollacliente',
            name='note',
            field=models.TextField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='bollacliente',
            name='numero_colli',
            field=models.PositiveIntegerField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='bollacliente',
            name='peso_lordo',
            field=models.CharField(null=True, max_length=50, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='bollacliente',
            name='peso_netto',
            field=models.CharField(null=True, max_length=50, blank=True),
            preserve_default=True,
        ),
    ]
