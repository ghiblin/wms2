# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0005_auto_20150127_1425'),
    ]

    operations = [
        migrations.AddField(
            model_name='dipendente',
            name='costo_orario',
            field=models.DecimalField(max_digits=5, default=0, decimal_places=2),
            preserve_default=False,
        ),
    ]
