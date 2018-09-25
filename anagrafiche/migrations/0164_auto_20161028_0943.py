# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0163_auto_20161018_0849'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fatturacliente',
            name='commessa',
            field=models.ForeignKey(blank=True, related_name='fatture_clienti', to='anagrafiche.Commessa', null=True),
        ),
    ]
