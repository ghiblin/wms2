# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0080_auto_20150409_0939'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contocorrente',
            name='nome_banca',
            field=models.CharField(max_length=60),
        ),
    ]
