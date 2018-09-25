# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0135_auto_20151014_1013'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fatturafornitore',
            name='aliquota_IVA',
            field=models.ForeignKey(blank=True, null=True, help_text='Può valere Null quando si crea partendo da una bolla.', to='anagrafiche.AliquotaIVA'),
        ),
    ]
