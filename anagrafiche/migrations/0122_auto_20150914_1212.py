# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0121_auto_20150911_1740'),
    ]

    operations = [
        migrations.AddField(
            model_name='bollacliente',
            name='fatturata',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='rigabollacliente',
            name='fatturata',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
