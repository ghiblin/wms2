# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0129_auto_20151007_1554'),
    ]

    operations = [
        migrations.AddField(
            model_name='rigafatturacliente',
            name='sconto',
            field=models.DecimalField(default=0, decimal_places=2, max_digits=5),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='rigaordinecliente',
            name='sconto',
            field=models.DecimalField(default=0, decimal_places=2, max_digits=5),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='rigapreventivocliente',
            name='sconto',
            field=models.DecimalField(default=0, decimal_places=2, max_digits=5),
            preserve_default=True,
        ),
    ]
