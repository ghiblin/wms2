# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0040_auto_20150304_1225'),
    ]

    operations = [
        migrations.AlterField(
            model_name='entita',
            name='costo_riba',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=4),
        ),
    ]
