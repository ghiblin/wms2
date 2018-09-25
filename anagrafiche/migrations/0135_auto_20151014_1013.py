# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0134_auto_20151013_1921'),
    ]

    operations = [
        migrations.AlterField(
            model_name='preventivofornitore',
            name='data_preventivo_fornitore',
            field=models.DateField(null=True),
        ),
    ]
