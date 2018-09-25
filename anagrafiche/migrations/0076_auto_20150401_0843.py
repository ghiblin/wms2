# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0075_auto_20150401_0840'),
    ]

    operations = [
        migrations.AddField(
            model_name='articolo',
            name='lt',
            field=models.PositiveIntegerField(null=True, help_text='Lead time', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='articolo',
            name='ss',
            field=models.DecimalField(max_digits=7, decimal_places=2, null=True, help_text='scorta di sicurezza', blank=True),
            preserve_default=True,
        ),
    ]
