# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0143_auto_20151120_1457'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bollafornitore',
            name='causale_trasporto',
            field=models.ForeignKey(default=1, to='anagrafiche.TipoCausaleTrasporto'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='bollafornitore',
            name='peso_lordo',
            field=models.CharField(max_length=50, default='0', blank=True),
        ),
        migrations.AlterField(
            model_name='bollafornitore',
            name='peso_netto',
            field=models.CharField(max_length=50, default='0', blank=True),
        ),
        migrations.AlterField(
            model_name='bollafornitore',
            name='trasporto_a_cura',
            field=models.ForeignKey(default=3, to='anagrafiche.TipoTrasportoACura'),
            preserve_default=False,
        ),
    ]
