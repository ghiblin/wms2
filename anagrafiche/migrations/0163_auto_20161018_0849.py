# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0162_auto_20161010_1338'),
    ]

    operations = [
        migrations.AlterField(
            model_name='aliquotaiva',
            name='percentuale',
            field=models.DecimalField(decimal_places=2, max_digits=5),
        ),
    ]
