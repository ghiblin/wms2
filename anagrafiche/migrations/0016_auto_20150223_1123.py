# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0015_auto_20150223_1051'),
    ]

    operations = [
        migrations.AlterField(
            model_name='commessa',
            name='prodotto',
            field=models.TextField(blank=True, null=True),
        ),
    ]
