# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0130_auto_20151009_0943'),
    ]

    operations = [
        migrations.RenameField(
            model_name='rigafatturacliente',
            old_name='sconto',
            new_name='sconto_percentuale',
        ),
        migrations.RenameField(
            model_name='rigaordinecliente',
            old_name='sconto',
            new_name='sconto_percentuale',
        ),
        migrations.RenameField(
            model_name='rigapreventivocliente',
            old_name='sconto',
            new_name='sconto_percentuale',
        ),
    ]
