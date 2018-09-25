# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0011_cliente_cancellato'),
    ]

    operations = [
        migrations.AddField(
            model_name='commessa',
            name='cancellato',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
