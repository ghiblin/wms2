# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0099_ordinecliente_aliquota_iva'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rigapreventivocliente',
            name='quantita',
            field=models.DecimalField(verbose_name='quantità', max_digits=8, decimal_places=2),
        ),
    ]
