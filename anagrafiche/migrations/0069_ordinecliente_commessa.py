# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0068_auto_20150319_1053'),
    ]

    operations = [
        migrations.AddField(
            model_name='ordinecliente',
            name='commessa',
            field=models.ForeignKey(null=True, related_name='ordini_clienti', to='anagrafiche.Commessa'),
            preserve_default=True,
        ),
    ]
