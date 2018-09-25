# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0073_auto_20150323_0110'),
    ]

    operations = [
        migrations.AddField(
            model_name='commessa',
            name='data_consegna',
            field=models.DateField(blank=True, null=True),
            preserve_default=True,
        ),
    ]
