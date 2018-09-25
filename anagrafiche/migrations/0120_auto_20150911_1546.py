# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0119_fatturacliente_rigafatturacliente'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rigafatturacliente',
            name='note',
            field=models.CharField(default='', max_length=500, blank=True),
        ),
    ]
