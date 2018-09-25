# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0061_auto_20150313_1833'),
    ]

    operations = [
        migrations.AddField(
            model_name='ordinecliente',
            name='descrizione',
            field=models.CharField(null=True, max_length=100, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='ordinecliente',
            name='note',
            field=models.TextField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
