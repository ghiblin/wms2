# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0164_auto_20161028_0943'),
    ]

    operations = [
        migrations.AddField(
            model_name='ordinecliente',
            name='riferimento_cliente',
            field=models.CharField(max_length=150, null=True, blank=True, default=''),
        ),
    ]
