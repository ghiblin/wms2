# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0078_dipendente_salta_validazione_cf'),
    ]

    operations = [
        migrations.AlterField(
            model_name='articolo',
            name='unita_di_misura',
            field=models.CharField(max_length=2, choices=[('PZ', 'pz'), ('NR', 'nr'), ('SC', 'sc'), ('ME', 'm'), ('M2', 'm²'), ('CM', 'cm'), ('MM', 'mm'), ('KG', 'kg'), ('HG', 'hg'), ('LI', 'l')]),
        ),
    ]
