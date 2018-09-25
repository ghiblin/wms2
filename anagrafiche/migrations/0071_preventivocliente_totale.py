# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0070_auto_20150319_1108'),
    ]

    operations = [
        migrations.AddField(
            model_name='preventivocliente',
            name='totale',
            field=models.DecimalField(default=0, decimal_places=2, max_digits=8),
            preserve_default=True,
        ),
    ]
