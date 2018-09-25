# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0098_auto_20150519_2344'),
    ]

    operations = [
        migrations.AddField(
            model_name='ordinecliente',
            name='aliquota_IVA',
            field=models.ForeignKey(to='anagrafiche.AliquotaIVA', blank=True, null=True),
            preserve_default=True,
        ),
    ]
