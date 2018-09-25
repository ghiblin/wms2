# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0062_auto_20150315_1007'),
    ]

    operations = [
        migrations.AddField(
            model_name='rigaordinecliente',
            name='totale',
            field=models.DecimalField(default=0, decimal_places=2, max_digits=7),
            preserve_default=False,
        ),
    ]
