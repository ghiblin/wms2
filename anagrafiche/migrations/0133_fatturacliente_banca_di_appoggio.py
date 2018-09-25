# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0132_auto_20151009_1348'),
    ]

    operations = [
        migrations.AddField(
            model_name='fatturacliente',
            name='banca_di_appoggio',
            field=models.ForeignKey(null=True, to='anagrafiche.ContoCorrente', blank=True),
            preserve_default=True,
        ),
    ]
