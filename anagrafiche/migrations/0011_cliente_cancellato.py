# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0010_auto_20150209_1041'),
    ]

    operations = [
        migrations.AddField(
            model_name='cliente',
            name='cancellato',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
