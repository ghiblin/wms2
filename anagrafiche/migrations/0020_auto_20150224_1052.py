# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0019_auto_20150224_1048'),
    ]

    operations = [
        migrations.RenameField(
            model_name='contocorrente',
            old_name='preferita',
            new_name='predefinito',
        ),
    ]
