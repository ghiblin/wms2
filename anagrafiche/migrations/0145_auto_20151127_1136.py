# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0144_auto_20151120_1505'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bollacliente',
            name='peso_lordo',
            field=models.CharField(default='0', null=True, max_length=50, blank=True),
        ),
        migrations.AlterField(
            model_name='bollacliente',
            name='peso_netto',
            field=models.CharField(default='0', null=True, max_length=50, blank=True),
        ),
    ]
