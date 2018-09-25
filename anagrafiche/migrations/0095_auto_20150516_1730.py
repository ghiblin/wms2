# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0094_rigapreventivocliente_accettato'),
    ]

    operations = [
        migrations.RenameField(
            model_name='rigapreventivocliente',
            old_name='accettato',
            new_name='accettata',
        ),
    ]
