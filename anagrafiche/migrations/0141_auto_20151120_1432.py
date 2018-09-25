# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0140_auto_20151114_1829'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bollacliente',
            name='causale_trasporto',
            field=models.ForeignKey(to='anagrafiche.TipoCausaleTrasporto', default=1),
        ),
        migrations.AlterField(
            model_name='bollacliente',
            name='peso_lordo',
            field=models.CharField(max_length=50, default='0', blank=True),
        ),
        migrations.AlterField(
            model_name='bollacliente',
            name='peso_netto',
            field=models.CharField(max_length=50, default='0', blank=True),
        ),
        migrations.AlterField(
            model_name='bollacliente',
            name='trasporto_a_cura',
            field=models.ForeignKey(to='anagrafiche.TipoTrasportoACura', default=3),
        ),
    ]
