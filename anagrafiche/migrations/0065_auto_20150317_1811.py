# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0064_auto_20150316_1503'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='contocorrente',
            name='italiano',
        ),
        migrations.AddField(
            model_name='contocorrente',
            name='straniero',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
