# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0028_auto_20150302_1700'),
    ]

    operations = [
        migrations.RenameField(
            model_name='contocorrente',
            old_name='cliente',
            new_name='entita',
        ),
    ]
