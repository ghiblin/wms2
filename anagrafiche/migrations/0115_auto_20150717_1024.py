# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0114_auto_20150716_1729'),
    ]

    operations = [
        migrations.AddField(
            model_name='ordinecliente',
            name='bollettato',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='rigaordinecliente',
            name='bollettata',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
