# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0004_auto_20150127_1424'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tipolavoro',
            name='descrizione',
            field=models.CharField(unique=True, max_length=50),
        ),
    ]
