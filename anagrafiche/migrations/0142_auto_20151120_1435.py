# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0141_auto_20151120_1432'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bollacliente',
            name='trasporto_a_cura',
            field=models.ForeignKey(default=3, to='anagrafiche.TipoTrasportoACura'),
        ),
    ]
