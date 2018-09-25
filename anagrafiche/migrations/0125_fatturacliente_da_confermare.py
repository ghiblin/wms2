# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0124_auto_20150918_0935'),
    ]

    operations = [
        migrations.AddField(
            model_name='fatturacliente',
            name='da_confermare',
            field=models.BooleanField(default=False, help_text='campo settato a True quando la fattura è creata con valori di default'),
            preserve_default=True,
        ),
    ]
