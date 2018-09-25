# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0139_auto_20151106_0900'),
    ]

    operations = [
        migrations.AlterField(
            model_name='aliquotaiva',
            name='percentuale',
            field=models.DecimalField(max_digits=5, unique=True, decimal_places=2),
        ),
        migrations.AlterField(
            model_name='tipopagamento',
            name='descrizione',
            field=models.CharField(max_length=250, unique=True),
        ),
    ]
