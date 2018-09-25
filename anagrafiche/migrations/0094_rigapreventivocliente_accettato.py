# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0093_auto_20150514_0411'),
    ]

    operations = [
        migrations.AddField(
            model_name='rigapreventivocliente',
            name='accettato',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
