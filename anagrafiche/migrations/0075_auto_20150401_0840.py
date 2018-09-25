# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0074_commessa_data_consegna'),
    ]

    operations = [
        migrations.AlterField(
            model_name='articolo',
            name='unita_di_misura',
            field=models.CharField(max_length=2, choices=[('PZ', 'pz'), ('ME', 'm'), ('M2', 'm²'), ('CM', 'cm'), ('KG', 'kg'), ('HG', 'hg'), ('LI', 'l'), ('SC', 'sc')]),
        ),
    ]
