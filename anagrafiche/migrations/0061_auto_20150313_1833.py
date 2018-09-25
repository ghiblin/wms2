# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0060_auto_20150312_0949'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='rigapreventivocliente',
            name='commessa',
        ),
        migrations.AddField(
            model_name='rigapreventivocliente',
            name='totale',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=7),
            preserve_default=False,
        ),
    ]
