# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0048_auto_20150308_1559'),
    ]

    operations = [
        migrations.AddField(
            model_name='entita',
            name='straniero',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
