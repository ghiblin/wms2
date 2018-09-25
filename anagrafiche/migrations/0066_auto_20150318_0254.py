# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0065_auto_20150317_1811'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rigaordinecliente',
            name='commessa',
            field=models.ForeignKey(to='anagrafiche.Commessa', null=True, blank=True),
        ),
    ]
