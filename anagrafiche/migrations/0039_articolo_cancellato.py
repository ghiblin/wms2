# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0038_articolo'),
    ]

    operations = [
        migrations.AddField(
            model_name='articolo',
            name='cancellato',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
