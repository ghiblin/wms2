# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0043_codiceiva'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='CodiceIVA',
            new_name='AliquotaIVA',
        ),
        migrations.AlterModelOptions(
            name='aliquotaiva',
            options={'verbose_name_plural': 'aliquote IVA'},
        ),
    ]
