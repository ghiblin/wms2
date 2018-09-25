# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0069_ordinecliente_commessa'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ordinecliente',
            name='commessa',
            field=models.ForeignKey(to='anagrafiche.Commessa', related_name='ordini_clienti'),
        ),
    ]
