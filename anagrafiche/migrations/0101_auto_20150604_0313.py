# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0100_auto_20150604_0310'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ordinecliente',
            name='totale',
            field=models.DecimalField(default=0, max_digits=9, decimal_places=2),
        ),
        migrations.AlterField(
            model_name='preventivocliente',
            name='totale',
            field=models.DecimalField(default=0, max_digits=9, decimal_places=2),
        ),
        migrations.AlterField(
            model_name='rigaordinecliente',
            name='quantita',
            field=models.DecimalField(verbose_name='quantità', max_digits=8, decimal_places=2),
        ),
        migrations.AlterField(
            model_name='rigaordinecliente',
            name='totale',
            field=models.DecimalField(max_digits=9, decimal_places=2),
        ),
        migrations.AlterField(
            model_name='rigapreventivocliente',
            name='totale',
            field=models.DecimalField(max_digits=9, decimal_places=2),
        ),
    ]
