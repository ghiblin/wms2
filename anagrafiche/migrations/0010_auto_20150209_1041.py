# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0009_commessa_data_apertura'),
    ]

    operations = [
        migrations.AlterField(
            model_name='commessa',
            name='data_apertura',
            field=models.DateField(default='2015-01-01'),
        ),
    ]
