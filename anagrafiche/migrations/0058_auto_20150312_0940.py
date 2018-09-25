# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0057_auto_20150312_0907'),
    ]

    operations = [
        migrations.AddField(
            model_name='rigapreventivocliente',
            name='articolo_descrizione',
            field=models.CharField(default='', max_length=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='rigapreventivocliente',
            name='articolo_prezzo',
            field=models.DecimalField(max_digits=7, decimal_places=2, default=5),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='rigapreventivocliente',
            name='note',
            field=models.CharField(null=True, blank=True, max_length=200),
            preserve_default=True,
        ),
    ]
