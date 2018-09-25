# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0142_auto_20151120_1435'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bollacliente',
            name='causale_trasporto',
            field=models.ForeignKey(to='anagrafiche.TipoCausaleTrasporto'),
        ),
        migrations.AlterField(
            model_name='bollacliente',
            name='trasporto_a_cura',
            field=models.ForeignKey(to='anagrafiche.TipoTrasportoACura'),
        ),
    ]
